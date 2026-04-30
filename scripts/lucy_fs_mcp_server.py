#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
HELPER_PATH = SCRIPT_PATH.parent / "lucy_fs_readonly.py"
PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "lucy-fs-readonly", "version": "0.1.0"}

TOOLS = {
    "lucy_find_files": {
        "description": "Find files by relative filename fragment inside the Doctor-Lucy repository.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "minimum": 1, "maximum": 50},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    "lucy_grep_text": {
        "description": "Search text inside allowed repository files and return matching lines.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "path": {"type": "string"},
                "max_results": {"type": "integer", "minimum": 1, "maximum": 50},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    "lucy_read_lines": {
        "description": "Read an exact line range from one allowed repository file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "start": {"type": "integer", "minimum": 1},
                "end": {"type": "integer", "minimum": 1},
            },
            "required": ["path", "start", "end"],
            "additionalProperties": False,
        },
    },
}


class McpError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def compact_json(payload):
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def send_message(message):
    body = json.dumps(message, ensure_ascii=False).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
    sys.stdout.buffer.write(header)
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def read_message():
    headers = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        name, _, value = line.decode("utf-8").partition(":")
        headers[name.strip().lower()] = value.strip()
    length = int(headers.get("content-length", "0"))
    if length <= 0:
        return None
    payload = sys.stdin.buffer.read(length)
    if not payload:
        return None
    return json.loads(payload.decode("utf-8"))


def make_response(request_id, result=None, error=None):
    response = {"jsonrpc": "2.0", "id": request_id}
    if error is not None:
        response["error"] = error
    else:
        response["result"] = result
    return response


def coerce_string(value, field):
    if not isinstance(value, str) or not value.strip():
        raise McpError(-32602, f"{field} must be a non-empty string")
    return value


def coerce_int(value, field):
    if not isinstance(value, int):
        raise McpError(-32602, f"{field} must be an integer")
    return value


def call_helper(action, arguments):
    cmd = [sys.executable, str(HELPER_PATH), action]
    if action == "find_files":
        cmd.extend(["--query", coerce_string(arguments.get("query"), "query")])
        if "max_results" in arguments:
            cmd.extend(["--max-results", str(coerce_int(arguments["max_results"], "max_results"))])
    elif action == "grep_text":
        cmd.extend(["--query", coerce_string(arguments.get("query"), "query")])
        if "path" in arguments:
            cmd.extend(["--path", coerce_string(arguments["path"], "path")])
        if "max_results" in arguments:
            cmd.extend(["--max-results", str(coerce_int(arguments["max_results"], "max_results"))])
    elif action == "read_lines":
        cmd.extend(
            [
                "--path",
                coerce_string(arguments.get("path"), "path"),
                "--start",
                str(coerce_int(arguments.get("start"), "start")),
                "--end",
                str(coerce_int(arguments.get("end"), "end")),
            ]
        )
    else:
        raise McpError(-32601, f"unknown helper action: {action}")

    completed = subprocess.run(cmd, capture_output=True, text=True, cwd=str(SCRIPT_PATH.parent.parent), check=False)
    stdout = completed.stdout.strip()
    if not stdout:
        payload = {"ok": False, "error": "helper returned empty output"}
    else:
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            payload = {"ok": False, "error": "helper returned non-json output", "raw": stdout[:500]}
    is_error = completed.returncode != 0 or not payload.get("ok", False)
    return payload, is_error


def handle_initialize(_params):
    return {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {"tools": {"listChanged": False}},
        "serverInfo": SERVER_INFO,
    }


def handle_tools_list():
    return {
        "tools": [
            {"name": name, "description": meta["description"], "inputSchema": meta["inputSchema"]}
            for name, meta in TOOLS.items()
        ]
    }


def handle_tools_call(params):
    if not isinstance(params, dict):
        raise McpError(-32602, "tools/call params must be an object")
    name = params.get("name")
    arguments = params.get("arguments", {})
    if name not in TOOLS:
        raise McpError(-32601, f"unknown tool: {name}")
    if not isinstance(arguments, dict):
        raise McpError(-32602, "tool arguments must be an object")

    action = name.replace("lucy_", "", 1)
    payload, is_error = call_helper(action, arguments)
    return {
        "content": [{"type": "text", "text": compact_json(payload)}],
        "isError": is_error,
    }


def handle_request(message):
    method = message.get("method")
    request_id = message.get("id")
    if method == "initialize":
        return make_response(request_id, handle_initialize(message.get("params")))
    if method == "tools/list":
        return make_response(request_id, handle_tools_list())
    if method == "tools/call":
        return make_response(request_id, handle_tools_call(message.get("params")))
    if request_id is None:
        return None
    raise McpError(-32601, f"method not found: {method}")


def serve():
    while True:
        message = read_message()
        if message is None:
            return 0
        try:
            response = handle_request(message)
        except McpError as exc:
            if message.get("id") is not None:
                response = make_response(message["id"], error={"code": exc.code, "message": exc.message})
            else:
                response = None
        except Exception as exc:  # pragma: no cover - defensive
            if message.get("id") is not None:
                response = make_response(message["id"], error={"code": -32603, "message": str(exc)})
            else:
                response = None
        if response is not None:
            send_message(response)


def build_parser():
    return argparse.ArgumentParser(description="Minimal MCP stdio wrapper for lucy_fs_readonly.py")


def main():
    parser = build_parser()
    parser.parse_args()
    raise SystemExit(serve())


if __name__ == "__main__":
    main()
