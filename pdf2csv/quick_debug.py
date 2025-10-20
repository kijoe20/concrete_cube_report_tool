#!/usr/bin/env python3
"""Quick PDF text viewer"""
import sys
import pdfplumber

if len(sys.argv) < 2:
    print("Usage: python quick_debug.py <pdf_file> [page_number]")
    sys.exit(1)

pdf_path = sys.argv[1]
page_num = int(sys.argv[2]) - 1 if len(sys.argv) > 2 else 0

with pdfplumber.open(pdf_path) as pdf:
    if page_num < len(pdf.pages):
        text = pdf.pages[page_num].extract_text()
        print(f"PAGE {page_num + 1}:")
        print("="*80)
        print(text)
        print("="*80)
        print(f"\nCharacters: {len(text)}")
        print(f"Lines: {text.count(chr(10))}")
    else:
        print(f"Error: Page {page_num + 1} doesn't exist")
        print(f"PDF has {len(pdf.pages)} pages")
