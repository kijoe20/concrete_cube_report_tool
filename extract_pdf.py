import fitz  # PyMuPDF
import re

def extract_cube_data(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    cube_rows = []
    for page in doc:
        text = page.get_text()
        report_no_match = re.search(r'Report no.[:\n]*\*([A-Z0-9]+)\*', text)
        report_no = report_no_match.group(1) if report_no_match else ""

        date_cast_match = re.search(r'Date Cast *: *([0-9]{2}-[A-Za-z]{3}-[0-9]{4})', text)
        date_cast = date_cast_match.group(1) if date_cast_match else ""

        pour_loc_match = re.search(r'Pour Location *: *([\s\S]+?)\n(?:Date Cast|Mix ID)', text)
        pour_location = pour_loc_match.group(1).strip() if pour_loc_match else ""

        cube_lines = re.findall(r'(CU\d{6,})\s+(\d{8}-\d{2}D-[\w\-/]+)\s+([\w/\+]+)\s+[\d\.]+\s+[\d\.]+\s+([\d\.]+)', text)
        for line in cube_lines:
            cube_id, cube_mark, grade, strength = line
            parts = re.split("[-]", cube_mark)
            if len(parts) >= 4:
                cube_prefix = "-".join(parts[:3]) + "-"
                cube_no = parts[3][:-1]
                cube_suffix = parts[3][-1]
            else:
                cube_prefix, cube_no, cube_suffix = cube_mark, "", ""
            cube_rows.append({
                "B": cube_prefix,
                "C": cube_no,
                "D": cube_suffix,
                "E": report_no,
                "F": date_cast,
                "H": strength,
                "O": pour_location
            })
    return cube_rows, None
