import re
import streamlit as st

def extract_cube_data_from_text(text_content):
    """
    Extract cube data from pasted text content.
    This function is specifically designed for the text input mode.
    """
    try:
        all_cube_rows = []
        
        # Debug: Show text preview
        st.write("### Debug: Text Content Preview")
        st.text(text_content[:1000] + "..." if len(text_content) > 1000 else text_content)
        
        # Split text into individual reports
        reports = split_into_reports(text_content)
        st.write(f"Found {len(reports)} individual reports")
        
        for report_idx, report_text in enumerate(reports):
            st.write(f"### Processing Report {report_idx + 1}")
            
            # Extract basic info for this report
            report_info = extract_report_info(report_text)
            
            # Extract cube data for this report
            cube_rows = extract_cube_data_from_report(report_text, report_info)
            
            all_cube_rows.extend(cube_rows)
            st.write(f"Extracted {len(cube_rows)} cube entries from report {report_idx + 1}")
        
        st.write(f"Total cube rows extracted: {len(all_cube_rows)}")
        
        # Show extracted data for verification
        if all_cube_rows:
            st.write("### Extracted Data Preview:")
            for i, row in enumerate(all_cube_rows[:10]):  # Show first 10 rows
                st.write(f"Row {i+1}: {row}")
        else:
            st.error("No cube data extracted. Please check the text format.")
        
        return all_cube_rows
        
    except Exception as e:
        st.error(f"Error extracting text data: {str(e)}")
        import traceback
        st.write(f"Traceback: {traceback.format_exc()}")
        return []

def split_into_reports(text_content):
    """Split text into individual reports based on report headers."""
    # Look for report headers
    report_pattern = r'Material Tech Company Limited.*?TEST REPORT'
    report_matches = list(re.finditer(report_pattern, text_content, re.DOTALL))
    
    reports = []
    for i, match in enumerate(report_matches):
        start_pos = match.start()
        if i + 1 < len(report_matches):
            end_pos = report_matches[i + 1].start()
        else:
            end_pos = len(text_content)
        
        report_text = text_content[start_pos:end_pos]
        reports.append(report_text.strip())
    
    # If no reports found, treat entire text as one report
    if not reports:
        reports = [text_content]
    
    return reports

def extract_report_info(report_text):
    """Extract basic information from a single report."""
    info = {
        'report_no': '',
        'date_cast': '',
        'pour_location': ''
    }
    
    # Extract Report Number
    report_patterns = [
        r'Report\s*no\.?\s*:?\s*\n\s*(\d+CU\d+)',
        r'Report\s*no\.?\s*:?\s*(\d+CU\d+)',
        r'(\d+CU\d+)',
        r'\*(\d+CU\d+)\*'
    ]
    
    for pattern in report_patterns:
        match = re.search(pattern, report_text, re.IGNORECASE)
        if match:
            info['report_no'] = match.group(1)
            break
    
    # Extract Date Cast
    date_patterns = [
        r'Date\s*Cast\s*:?\s*([0-9]{2}-[A-Za-z]{3}-[0-9]{4})',
        r'Cast\s*Date\s*:?\s*([0-9]{2}-[A-Za-z]{3}-[0-9]{4})',
        r'([0-9]{2}-[A-Za-z]{3}-[0-9]{4})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, report_text, re.IGNORECASE)
        if match:
            info['date_cast'] = match.group(1)
            break
    
    # Extract Pour Location
    pour_patterns = [
        r'Pour\s*Location\s*:?\s*([^\n]+)',
        r'Location\s*:?\s*([^\n]+)'
    ]
    
    for pattern in pour_patterns:
        match = re.search(pattern, report_text, re.IGNORECASE)
        if match:
            info['pour_location'] = match.group(1).strip()
            break
    
    return info

def extract_cube_data_from_report(report_text, report_info):
    """Extract cube data from a single report using table structure analysis."""
    cube_rows = []
    
    # Find the table section by looking for headers
    table_start = report_text.find("Lab Cube ID")
    if table_start == -1:
        table_start = report_text.find("Customer Cube Mark")
    
    if table_start == -1:
        # Look for the first CU number as table start
        cu_match = re.search(r'(CU\d+)', report_text)
        if cu_match:
            table_start = cu_match.start()
    
    if table_start == -1:
        st.write("Could not find table start")
        return cube_rows
    
    # Extract the table section
    table_text = report_text[table_start:]
    st.write(f"Table section starts at position {table_start}")
    
    # Find all CU numbers and their cube marks in the table
    cu_mark_pattern = r'(CU\d+)\s+(\d{8}-\d{2}D-[A-Z]+-\d+[A-Z])'
    cu_mark_matches = re.findall(cu_mark_pattern, table_text)
    
    st.write(f"Found {len(cu_mark_matches)} CU-Mark pairs: {cu_mark_matches[:5]}...")
    
    # For each CU-Mark pair, find the associated strength value
    for cu_number, cube_mark in cu_mark_matches:
        # Parse cube mark
        if '-' in cube_mark:
            parts = cube_mark.split('-')
            if len(parts) >= 4:
                cube_prefix = "-".join(parts[:3]) + "-"
                cube_no = parts[3][:-1] if len(parts[3]) > 1 else parts[3]
                cube_suffix = parts[3][-1] if len(parts[3]) > 1 else ""
            else:
                cube_prefix, cube_no, cube_suffix = cube_mark, "", ""
        else:
            cube_prefix, cube_no, cube_suffix = cube_mark, "", ""
        
        # Find strength value for this specific CU-Mark pair
        strength_value = find_strength_for_cu_mark(table_text, cu_number, cube_mark)
        
        cube_rows.append({
            "B": cube_prefix,
            "C": cube_no,
            "D": cube_suffix,
            "E": report_info['report_no'],
            "F": report_info['date_cast'],
            "H": strength_value,
            "O": report_info['pour_location']
        })
        
        st.write(f"Extracted: {cu_number} - Mark: {cube_mark} - Strength: {strength_value}")
    
    return cube_rows

def find_strength_for_cu_mark(table_text, cu_number, cube_mark):
    """Find the strength value associated with a specific CU-Mark pair."""
    # Find the position of this specific CU-Mark pair
    search_pattern = f"{cu_number} {cube_mark}"
    cu_mark_pos = table_text.find(search_pattern)
    
    if cu_mark_pos == -1:
        return "0"
    
    # Look for strength values in the vicinity
    # Start searching from the position of the CU-Mark pair
    start_pos = cu_mark_pos
    end_pos = min(len(table_text), cu_mark_pos + 2000)  # Look ahead 2000 characters
    search_text = table_text[start_pos:end_pos]
    
    # Look for strength values in this section
    # First, try to find the strength column by looking for patterns
    strength_patterns = [
        r'\b([5-9][0-9]\.[0-9])\b',  # 50.0 to 99.9
        r'\b([1][0-9][0-9]\.[0-9])\b',  # 100.0 to 199.9
        r'\b([6-9][0-9]\.[0-9])\b',  # 60.0 to 99.9 (more specific)
    ]
    
    for pattern in strength_patterns:
        strength_matches = re.findall(pattern, search_text)
        for strength in strength_matches:
            try:
                strength_float = float(strength)
                if 50 <= strength_float <= 150:  # Reasonable concrete strength range
                    return strength
            except:
                continue
    
    # If no strength found with patterns, try a different approach
    # Look for numbers that appear after the CU-Mark pair
    lines = search_text.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        # Look for decimal numbers in this line
        numbers = re.findall(r'\b(\d+\.\d+)\b', line)
        for num in numbers:
            try:
                num_float = float(num)
                if 50 <= num_float <= 150:
                    return num
            except:
                continue
    
    return "0" 