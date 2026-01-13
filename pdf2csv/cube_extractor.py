#!/usr/bin/env python3
"""
Concrete Cube Test Report PDF to CSV Extractor

This script extracts concrete cube test data from PDF reports and converts it to CSV format.
Each cube's data is split into components and written as a pipe-delimited row.

Author: Automated Extraction Tool
Version: 1.0
"""

import re
import sys
from typing import List, Dict, Tuple, Optional

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber is not installed.")
    print("Please install it using: pip install pdfplumber")
    sys.exit(1)


def split_cube_mark(cube_mark: str) -> Tuple[str, str, str]:
    """
    Split cube mark into prefix, number, and suffix components.

    The cube mark format is typically: YYYYMMDD-TYPE-NUMBER-LETTER
    Examples:
        "20250621-45D-1A" -> ("20250621-45D-", "1", "A")
        "20250622-45DWP-11B" -> ("20250622-45DWP-", "11", "B")
        "20250623-60D-2A" -> ("20250623-60D-", "2", "A")

    Args:
        cube_mark: The complete cube mark string

    Returns:
        Tuple of (prefix, number, suffix)
        - prefix: Date and concrete type (e.g., "20250621-45D-")
        - number: Sequential cube number (e.g., "1", "11")
        - suffix: Cube variant letter (e.g., "A", "B")
    """
    # Pattern to match: prefix ending with dash, followed by digits, followed by single letter
    pattern = r'^(.+?-)(\d+)([A-Z])$'
    match = re.match(pattern, cube_mark)

    if match:
        prefix = match.group(1)
        number = match.group(2)
        suffix = match.group(3)
        return (prefix, number, suffix)

    # Fallback: return original as prefix with empty number and suffix
    print(f"Warning: Could not parse cube mark '{cube_mark}', using as-is")
    return (cube_mark, "", "")


def extract_report_number(text: str) -> str:
    """
    Extract the report number from page text.

    Looks for patterns like:
        - "Report No.: 04428CU763515"
        - "Report No: 04428CU763515"
        - "Report Number: 04428CU763515"

    Args:
        text: The page text content

    Returns:
        The report number or empty string if not found
    """
    patterns = [
        r'Report\s+No\.?:?\s*([A-Z0-9]+)',
        r'Report\s+Number:?\s*([A-Z0-9]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return ""


def extract_date_cast(text: str) -> str:
    """
    Extract the date cast from page text.

    Looks for patterns like:
        - "Date Cast: 02-Jul-2025"
        - "Date Cast 02-Jul-2025"

    Args:
        text: The page text content

    Returns:
        The date cast in DD-Mon-YYYY format or empty string if not found
    """
    pattern = r'(?:Date\s+Cast\s*:\s*)(\d{2}-[A-Za-z]{3}-\d{4})'
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return match.group(1)

    return ""


def extract_pour_location(text: str) -> str:
    """
    Extract the pour location from page text.

    Looks for patterns like:
        - "Location: 23/F-25/F Zone 2..."
        - "Pour Location: 23/F-25/F Zone 2..."

    Args:
        text: The page text content

    Returns:
        The pour location or empty string if not found
    """
    # Look for location field - it typically spans multiple lines
    patterns = [
        r'(?:Pour\sLocation\s*:\s*)(.+?)(?=\nDate\sCast)',  # Until next field
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            location = match.group(1).strip()
            # Clean up: remove extra whitespace and newlines, keep single spaces
            location = ' '.join(location.split())
            return location

    return ""


def extract_all_cubes_from_pdf(page_text: str, page_number: int) -> List[Dict[str, str]]:
    """
    Extract all cube test data from a single page.
    
    Handles following formats:
    Case 1: Suffix on same line
        CU058493 20250801-60D-6A 60/20D PFA 200 / 230 ... 795.6 79.2 S -
        
    Case 2: Suffix on next line
        CU058461 20250801-60D-11 60/20D PFA 200 / 235 ... 793.8 79.5 S -
        A
    
    Case 3: Base cube mark on one line, full identifier on next line
        CU058595 20250802-45DWP- 45/20 PFA+WP 150 / 160 ... 609.2 60.7 S -
        1A

    Case 4: Base cube mark on one line, full identifier on next line with dash
        CU058595 20250802-45DWP 45/20 PFA+WP 150 / 160 ... 609.2 60.7 S -
        -1A

    Case 5:Base cube mark on one line, full identifier on next next line
        CU804963 20251115-45DWP 45/20D PFA Krystaline 150 / 175 ... 649.4 64.7 S -
        Add Plus 2.5
        -1A

    Args:
        page_text: The extracted text from the PDF page
        page_number: The page number (for logging)
        
    Returns:
        List of dictionaries, each containing one cube's data
    """
    if not page_text:
        return []
    
    cubes = []
    
    # Extract page-level metadata (same for all cubes on the page)
    report_number = extract_report_number(page_text)
    date_cast = extract_date_cast(page_text)
    pour_location = extract_pour_location(page_text)
    
    # Split text into lines for line-by-line processing
    lines = page_text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # CASE 1: Complete cube mark with suffix on same line
        # Pattern: CU###### YYYYMMDD-TYPE-NUMBER-LETTER ... STRENGTH1 STRENGTH2 S -
        # Example: CU058493 20250801-60D-6A 60/20D PFA 200 / 230 100.1 x 100.2 x 100.2 2.413 2400 795.6 79.2 S -
        case1_match = re.search(
            r'CU\d+\s+(\d{8}-\d+[A-Z]+-\d+[A-Z])\s+.*?\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+S\s+-',
            line
        )
        
        if case1_match:
            full_cube_mark = case1_match.group(1)  # e.g., "20250801-60D-6A"
            strength = case1_match.group(3)         # Second number before "S -" (e.g., 79.2)
            
            prefix, number, suffix = split_cube_mark(full_cube_mark)
            
            cubes.append({
                'prefix': prefix,
                'number': number,
                'suffix': suffix,
                'report_number': report_number,
                'date_cast': date_cast,
                'strength': strength,
                'pour_location': pour_location
            })
            i += 1
            continue
        
        # CASE 2: Cube mark without suffix, suffix on next line
        # Pattern: CU###### YYYYMMDD-TYPE-NUMBER ... STRENGTH1 STRENGTH2 S -
        # Next line: LETTER
        # Example:
        #   CU058461 20250801-60D-11 60/20D PFA 200 / 235 99.8 x 99.9 x 99.9 2.409 2420 793.8 79.5 S -
        #   A
        case2_match = re.search(
            r'CU\d+\s+(\d{8}-\d+[A-Z]+-\d+)\s+.*?\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+S\s+-',
            line
        )
        
        if case2_match:
            # Check if next line exists and is a single letter
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                
                # Check if next line is exactly one alphabetic character
                if len(next_line) == 1 and next_line.isalpha() and next_line.isupper():
                    cube_mark_base = case2_match.group(1)  # e.g., "20250801-60D-11"
                    strength = case2_match.group(3)         # Second number (e.g., 79.5)
                    suffix = next_line                      # e.g., "A"
                    
                    # Construct full cube mark
                    full_cube_mark = f"{cube_mark_base}{suffix}"
                    
                    prefix, number, _ = split_cube_mark(full_cube_mark)
                    
                    cubes.append({
                        'prefix': prefix,
                        'number': number,
                        'suffix': suffix,
                        'report_number': report_number,
                        'date_cast': date_cast,
                        'strength': strength,
                        'pour_location': pour_location
                    })
                    
                    # Skip the next line since we've processed it
                    i += 2
                    continue
        
        # CASE 3: Base cube mark without number/suffix, full identifier on next line
        # Pattern: CU###### YYYYMMDD-TYPE- ... STRENGTH1 STRENGTH2 S -
        # Next line: NUMBER+LETTER
        # Example:
        #   CU058595 20250802-45DWP- 45/20 PFA+WP 150 / 160 100.2 x 100.2 x 100.1 2.406 2390 609.2 60.7 S -
        #   1A
        case3_match = re.search(
            r'CU\d+\s+(\d{8}-\d+[A-Z]+-)\s+.*?\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+S\s+-',
            line
        )
        
        if case3_match:
            # Check if next line exists and matches NUMBER+LETTER pattern
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                id_match = re.match(r'(\d+)([A-Z])$', next_line)
                
                if id_match:
                    cube_mark_base = case3_match.group(1)  # e.g., "20250802-45DWP-"
                    number = id_match.group(1)             # e.g., "1"
                    suffix = id_match.group(2)             # e.g., "A"
                    strength = case3_match.group(3)        # Second number (e.g., 60.7)
                    
                    cubes.append({
                        'prefix': cube_mark_base,
                        'number': number,
                        'suffix': suffix,
                        'report_number': report_number,
                        'date_cast': date_cast,
                        'strength': strength,
                        'pour_location': pour_location
                    })
                    
                    # Skip the next line since we've processed it
                    i += 2
                    continue

        # CASE 4: Base cube mark without number/suffix, full identifier on next line
        # Pattern: CU###### YYYYMMDD-TYPE- ... STRENGTH1 STRENGTH2 S -
        # Next line: "-"+NUMBER+LETTER
        # Example:
        #   CU058595 20250802-45DWP 45/20 PFA+WP 150 / 160 100.2 x 100.2 x 100.1 2.406 2390 609.2 60.7 S -
        #   -1A
        case4_match = re.search(
            r'CU\d+\s+(\d{8}-\d+[A-Z]+)\s+.*?\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+S\s+-',
            line
        )
        
        if case4_match:
            # Check if next line exists and matches "-"+NUMBER+LETTER pattern
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                id_match = re.match(r'-\s*(\d+)([A-Z])$', next_line)
                
                if id_match:
                    cube_mark_base = case4_match.group(1)  # e.g., "20250802-45DWP"
                    number = id_match.group(1)             # e.g., "1"
                    suffix = id_match.group(2)             # e.g., "A"
                    strength = case4_match.group(3)        # Second number (e.g., 60.7)
                    
                    # Construct full cube mark
                    full_cube_mark = f"{cube_mark_base}-{number}{suffix}"
                    prefix, _, _ = split_cube_mark(full_cube_mark)
                    
                    cubes.append({
                        'prefix': prefix,
                        'number': number,
                        'suffix': suffix,
                        'report_number': report_number,
                        'date_cast': date_cast,
                        'strength': strength,
                        'pour_location': pour_location
                    })
                    
                    # Skip the next line since we've processed it
                    i += 2
                    continue

        # CASE 5: Base cube mark without number/suffix, full identifier on next next line
        # Pattern: CU###### YYYYMMDD-TYPE- ... STRENGTH1 STRENGTH2 S -
        # Next line: Additional info (ignored)
        # Next next line: "-"+NUMBER+LETTER
        # Example:
        #   CU804963 20251115-45DWP 45/20D PFA Krystaline 150 / 175 100.0 x 100.1 x 100.2 2.410 2410 649.4 64.7 S -
        #   Add Plus 2.5
        #   -1A
        case5_match = re.search(
            r'CU\d+\s+(\d{8}-\d+[A-Z]+)\s+.*?\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+S\s+-',
            line
        )

        if case5_match:
            # Check if next next line exists and matches "-"+NUMBER+LETTER pattern
            if i + 2 < len(lines):
                next_line = lines[i + 1].strip()
                next_next_line = lines[i + 2].strip()
                id_match = re.match(r'-\s*(\d+)([A-Z])$', next_next_line)

                if id_match:
                    cube_mark_base = case5_match.group(1)  # e.g., "20251115-45DWP"
                    number = id_match.group(1)             # e.g., "1"
                    suffix = id_match.group(2)             # e.g., "A"
                    strength = case5_match.group(3)        # Second number (e.g., 64.7)

                    # Construct full cube mark
                    full_cube_mark = f"{cube_mark_base}-{number}{suffix}"
                    prefix, _, _ = split_cube_mark(full_cube_mark)

                    cubes.append({
                        'prefix': prefix,
                        'number': number,
                        'suffix': suffix,
                        'report_number': report_number,
                        'date_cast': date_cast,
                        'strength': strength,
                        'pour_location': pour_location
                    })

                    # Skip the next two lines since we've processed them
                    i += 3
                    continue

        # Move to next line if no match found
        i += 1
    
    return cubes


def write_csv_output(cubes: List[Dict[str, str]], output_path: str):
    """
    Write cube data to CSV file in pipe-delimited format.

    Args:
        cubes: List of cube data dictionaries
        output_path: Path to the output CSV file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for cube in cubes:
            # Format: Prefix|Number|Suffix|ReportNum|DateCast|Strength|Location
            line = (
                f"{cube['prefix']}|"
                f"{cube['number']}|"
                f"{cube['suffix']}|"
                f"{cube['report_number']}|"
                f"{cube['date_cast']}|"
                f"{cube['strength']}|"
                f"{cube['pour_location']}"
            )
            f.write(line + '\n')


def main():
    """Main execution function."""
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Concrete Cube Test Report PDF to CSV Extractor")
        print("")
        print("Usage:")
        print("  python cube_extractor.py <input_pdf> <output_csv>")
        print("")
        print("Example:")
        print("  python cube_extractor.py Prelim-202507.pdf output.csv")
        print("")
        sys.exit(1)

    input_pdf_path = sys.argv[1]
    output_csv_path = sys.argv[2]

    try:
        # Open PDF and extract text per page, then parse cubes
        print(f"Extracting data from: {input_pdf_path}")
        all_cubes = []

        with pdfplumber.open(input_pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text() or ""
                cubes = extract_all_cubes_from_pdf(page_text, page_number)
                if cubes:
                    print(f"Page {page_number}: {len(cubes)} cubes extracted")
                    all_cubes.extend(cubes)
                else:
                    print(f"Page {page_number}: No cubes found")

        if not all_cubes:
            print("\nWarning: No cube data extracted from PDF")
            print("Please check that the PDF contains the expected format")
            sys.exit(1)

        print(f"\nTotal cubes extracted: {len(all_cubes)}")

        # Write to CSV
        print(f"Writing data to: {output_csv_path}")
        write_csv_output(all_cubes, output_csv_path)

        print(f"\nSuccess! {len(all_cubes)} cube records written to {output_csv_path}")

    except FileNotFoundError:
        print(f"\nError: Input file '{input_pdf_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
