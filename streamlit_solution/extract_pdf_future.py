import fitz  # PyMuPDF
import re
import streamlit as st

def extract_cube_data(pdf_file):
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        cube_rows = []
        all_text = ""
        
        # Collect all text from all pages
        for page_num, page in enumerate(doc):
            text = page.get_text()
            all_text += f"\n--- PAGE {page_num + 1} ---\n{text}\n"
        
        # Debug: Show extracted text (first 1000 characters)
        st.write("### Debug: Extracted Text Preview")
        st.text(all_text[:1000] + "..." if len(all_text) > 1000 else all_text)
        
        # Extract Report Number - looking for the pattern like "02718CU763327"
        report_patterns = [
            r'Report\s*no\.?\s*:?\s*\n\s*(\d+CU\d+)',
            r'Report\s*no\.?\s*:?\s*(\d+CU\d+)',
            r'(\d+CU\d+)',
            r'\*(\d+CU\d+)\*'
        ]
        
        report_no = ""
        for pattern in report_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                report_no = match.group(1)
                st.write(f"Found Report Number: {report_no}")
                break
        
        # Extract Date Cast - looking for pattern like "04-Jun-2025"
        date_patterns = [
            r'Date\s*Cast\s*:?\s*([0-9]{2}-[A-Za-z]{3}-[0-9]{4})',
            r'Cast\s*Date\s*:?\s*([0-9]{2}-[A-Za-z]{3}-[0-9]{4})',
            r'([0-9]{2}-[A-Za-z]{3}-[0-9]{4})'
        ]
        
        date_cast = ""
        for pattern in date_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                date_cast = match.group(1)
                st.write(f"Found Date Cast: {date_cast}")
                break
        
        # Extract Pour Location - looking for pattern like "1/F Bearing Wall at G.L. P7～P8/ PP～PQ"
        pour_patterns = [
            r'Pour\s*Location\s*:?\s*([^\n]+)',
            r'Location\s*:?\s*([^\n]+)'
        ]
        
        pour_location = ""
        for pattern in pour_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                pour_location = match.group(1).strip()
                st.write(f"Found Pour Location: {pour_location}")
                break
        
        # NEW APPROACH: Direct regex extraction of cube data
        st.write("### Extracting Cube Data...")
        
        # Find all CU numbers in the text
        cu_numbers = re.findall(r'(CU\d+)', all_text)
        st.write(f"Found {len(cu_numbers)} CU numbers: {cu_numbers[:10]}...")  # Show first 10
        
        # Find all cube marks (the long identifiers)
        cube_marks = re.findall(r'(\d{8}-\d{2}D-[A-Z]+-\d+[A-Z])', all_text)
        st.write(f"Found {len(cube_marks)} cube marks: {cube_marks[:10]}...")  # Show first 10
        
        # Find all potential strength values (numbers between 20-150)
        strength_values = re.findall(r'\b([2-9][0-9]\.[0-9]|[1-9][0-9][0-9]\.[0-9])\b', all_text)
        st.write(f"Found {len(strength_values)} potential strength values: {strength_values[:10]}...")  # Show first 10
        
        # Create a mapping of CU numbers to cube marks
        cu_to_mark = {}
        for i, cu in enumerate(cu_numbers):
            if i < len(cube_marks):
                cu_to_mark[cu] = cube_marks[i]
        
        st.write(f"CU to Mark mapping: {dict(list(cu_to_mark.items())[:5])}")  # Show first 5
        
        # Extract cube data by finding CU numbers and their associated data
        for cu_number in cu_numbers:
            # Find the position of this CU number in the text
            cu_pos = all_text.find(cu_number)
            if cu_pos != -1:
                # Get the cube mark for this CU number
                cube_mark = cu_to_mark.get(cu_number, "")
                
                if cube_mark:
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
                    
                    # Find strength value near this CU entry
                    # Look in a 500 character window around the CU number
                    start_pos = max(0, cu_pos - 250)
                    end_pos = min(len(all_text), cu_pos + 250)
                    search_text = all_text[start_pos:end_pos]
                    
                    # Find strength values in this window
                    strength_matches = re.findall(r'\b([2-9][0-9]\.[0-9]|[1-9][0-9][0-9]\.[0-9])\b', search_text)
                    
                    strength_value = "0"
                    if strength_matches:
                        # Take the first reasonable strength value
                        for match in strength_matches:
                            try:
                                strength_float = float(match)
                                if 20 <= strength_float <= 150:
                                    strength_value = match
                                    break
                            except:
                                continue
                    
                    cube_rows.append({
                        "B": cube_prefix,
                        "C": cube_no,
                        "D": cube_suffix,
                        "E": report_no,
                        "F": date_cast,
                        "H": strength_value,
                        "O": pour_location
                    })
                    
                    st.write(f"Extracted: {cu_number} - Mark: {cube_mark} - Strength: {strength_value}")
        
        # If no data found with the above method, try alternative approach
        if not cube_rows:
            st.write("Trying alternative extraction method...")
            
            # Split text into lines and look for patterns
            lines = all_text.split('\n')
            
            # Find lines containing both CU numbers and strength values
            for i, line in enumerate(lines):
                if 'CU' in line:
                    # Extract CU number
                    cu_match = re.search(r'(CU\d+)', line)
                    if cu_match:
                        cu_number = cu_match.group(1)
                        
                        # Extract cube mark
                        mark_match = re.search(r'(\d{8}-\d{2}D-[A-Z]+-\d+[A-Z])', line)
                        if mark_match:
                            cube_mark = mark_match.group(1)
                            
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
                            
                            # Look for strength in current line or next few lines
                            strength_value = "0"
                            
                            # Check current line
                            strength_match = re.search(r'\b([2-9][0-9]\.[0-9]|[1-9][0-9][0-9]\.[0-9])\b', line)
                            if strength_match:
                                strength_value = strength_match.group(1)
                            
                            # Check next few lines if not found
                            if strength_value == "0":
                                for j in range(i+1, min(i+5, len(lines))):
                                    next_line = lines[j]
                                    strength_match = re.search(r'\b([2-9][0-9]\.[0-9]|[1-9][0-9][0-9]\.[0-9])\b', next_line)
                                    if strength_match:
                                        strength_value = strength_match.group(1)
                                        break
                            
                            cube_rows.append({
                                "B": cube_prefix,
                                "C": cube_no,
                                "D": cube_suffix,
                                "E": report_no,
                                "F": date_cast,
                                "H": strength_value,
                                "O": pour_location
                            })
                            
                            st.write(f"Alternative extraction: {cu_number} - Mark: {cube_mark} - Strength: {strength_value}")
        
        st.write(f"Total cube rows extracted: {len(cube_rows)}")
        
        # Show extracted data for verification
        if cube_rows:
            st.write("### Extracted Data Preview:")
            for i, row in enumerate(cube_rows[:5]):  # Show first 5 rows
                st.write(f"Row {i+1}: {row}")
        else:
            st.error("No cube data extracted. Please check the PDF format.")
            st.write("### Debug Information:")
            st.write(f"Total text length: {len(all_text)}")
            st.write(f"Number of lines: {len(all_text.split(chr(10)))}")
            st.write("First 20 lines:")
            for i, line in enumerate(all_text.split(chr(10))[:20]):
                st.write(f"Line {i+1}: {line}")
        
        return cube_rows, all_text
        
    except Exception as e:
        st.error(f"Error extracting PDF data: {str(e)}")
        import traceback
        st.write(f"Traceback: {traceback.format_exc()}")
        return [], None
