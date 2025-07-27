import re

def extract_from_text(text: str):
    data = []

    # Report No.
    report_match = re.search(r'Report no.\*([A-Z0-9]+)\*', text)
    report_no = report_match.group(1) if report_match else ""

    # Pour Location
    loc_match = re.search(r'Pour Location\s*:\s*(.+)', text)
    pour_location = loc_match.group(1).strip() if loc_match else ""

    # Date Cast
    date_match = re.search(r'Date Cast\s*:\s*([0-9]{2}-[A-Za-z]{3}-[0-9]{4})', text)
    date_cast = date_match.group(1) if date_match else ""

    # Cube lines (CUxxxxx ...)
    lines = text.splitlines()
    for line in lines:
        if line.startswith("CU"):
            parts = line.split()
            if len(parts) >= 10:
                cube_mark = parts[1]
                strength = parts[-2]  # e.g., 74.6

                # Split cube mark
                mark_match = re.match(r"(\d{8}-\d{2}D-)(\d+)([A-Z])", cube_mark)
                if mark_match:
                    B, C, D = mark_match.groups()
                    data.append({
                        "B": B,
                        "C": C,
                        "D": D,
                        "E": report_no,
                        "F": date_cast,
                        "H": float(strength),
                        "O": pour_location
                    })

    return data
