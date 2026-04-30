#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parent / "lucy_fs_mcp_server.py"


def send_message(proc, payload):
    body = json.dumps(payload).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    proc.stdin.write(header)
    proc.stdin.write(body)
    proc.stdin.flush()


def read_message(proc):
    headers = {}
    while True:
        line = proc.stdout.readline()
        if not line:
            raise RuntimeError("server closed stdout unexpectedly")
        if line in (b"\r\n", b"\n"):
            break
        name, _, value = line.decode("utf-8").partition(":")
        headers[name.strip().lower()] = value.strip()
    length = int(headers["content-length"])
    payload = proc.stdout.read(length)
    return json.loads(payload.decode("utf-8"))


def request(proc, request_id, method, params=None):
    payload = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        payload["params"] = params
    send_message(proc, payload)
    return read_message(proc)


def expect(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    proc = subprocess.Popen(
        [sys.executable, str(SCRIPT_PATH)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        init = request(proc, 1, "initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "0.1"}})
        expect(init["result"]["serverInfo"]["name"] == "lucy-fs-readonly", "initialize server name mismatch")

        send_message(proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

        tools = request(proc, 2, "tools/list", {})
        tool_names = [tool["name"] for tool in tools["result"]["tools"]]
        expect("lucy_grep_text" in tool_names, "lucy_grep_text missing from tools/list")
        expect("lucy_read_lines" in tool_names, "lucy_read_lines missing from tools/list")

        grep_resp = request(
            proc,
            3,
            "tools/call",
            {"name": "lucy_grep_text", "arguments": {"query": "delegate_mission", "path": "scripts", "max_results": 10}},
        )
        grep_payload = json.loads(grep_resp["result"]["content"][0]["text"])
        expect(grep_payload["ok"] is True, "grep_text payload not ok")
        expect(any(item["path"] == "scripts/lucy_openclaw_bridge.py" and item["line"] == 138 for item in grep_payload["results"]), "delegate_mission line not found")

        read_resp = request(
            proc,
            4,
            "tools/call",
            {"name": "lucy_read_lines", "arguments": {"path": "scripts/lucy_openclaw_bridge.py", "start": 138, "end": 168}},
        )
        read_payload = json.loads(read_resp["result"]["content"][0]["text"])
        expect(read_payload["ok"] is True, "read_lines payload not ok")
        expect(read_payload["lines"][0]["line"] == 138, "read_lines did not start at line 138")
        expect("def delegate_mission" in read_payload["lines"][0]["text"], "delegate_mission signature mismatch")

        bad_resp = request(
            proc,
            5,
            "tools/call",
            {"name": "lucy_read_lines", "arguments": {"path": "../.bashrc", "start": 1, "end": 2}},
        )
        expect(bad_resp["result"]["isError"] is True, "traversal request should be marked error")
        bad_payload = json.loads(bad_resp["result"]["content"][0]["text"])
        expect("parent traversal" in bad_payload["error"], "traversal rejection message missing")

        print("MCP wrapper test: OK")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


if __name__ == "__main__":
    main()
