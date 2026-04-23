#!/usr/bin/env python3
import sys
import os
from fpdf import FPDF

def convert_md_to_pdf(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        sys.exit(1)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Use a standard font that supports some symbols
    pdf.set_font("Arial", size=12)
    
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                pdf.ln(5)
                continue
            
            # Very basic MD parsing
            if line.startswith("# "):
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, line[2:], ln=True)
                pdf.set_font("Arial", size=12)
            elif line.startswith("## "):
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 9, line[3:], ln=True)
                pdf.set_font("Arial", size=12)
            elif line.startswith("* ") or line.startswith("- "):
                pdf.cell(10) # Indent
                pdf.cell(0, 7, f"- {line[2:]}", ln=True)
            elif line.startswith("**") and line.endswith("**"):
                 pdf.set_font("Arial", "B", 12)
                 pdf.cell(0, 7, line[2:-2], ln=True)
                 pdf.set_font("Arial", size=12)
            else:
                pdf.multi_cell(0, 7, line)
                # pdf.ln(2)

    pdf.output(output_path)
    print(f"Éxito: PDF generado en {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: md_to_pdf.py <input.md> <output.pdf>")
        sys.exit(1)
    
    convert_md_to_pdf(sys.argv[1], sys.argv[2])
