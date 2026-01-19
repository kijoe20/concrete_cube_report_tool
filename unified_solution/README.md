# Unified Concrete Cube Report Automation

This unified solution converts concrete cube PDF reports directly into formatted Excel workbooks in one command. It combines the existing PDF extraction logic with the Excel formatting workflow, removing the manual CSV import step.

## Requirements
- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation
```bash
pip install -r requirements.txt
```

## Usage

### Single PDF
```bash
python cube_automation.py input.pdf output.xlsx
```

### Batch Processing (Folder)
```bash
python cube_automation.py ./pdfs/ --folder --output-dir ./reports/
```

### Enable Validation
```bash
python cube_automation.py input.pdf output.xlsx --validate
```

## Windows Batch Wrapper
Use the included batch file for quick batch processing:
```bat
process_batch.bat
```

## Output Workbook Structure
The output Excel file contains:
- **Raw** sheet with all extracted data
- **45D**, **60D**, **45DWP**, **60DWP** sheets with:
  - Merged pour locations (column G)
  - Merged every two rows for columns A, B, D, E (matching legacy output)

## Data Format (Raw Sheet)
Columns:
1. Cube Mark Prefix
2. Cube Number
3. Cube Suffix
4. Report Number
5. Date Cast
6. Compressive Strength (MPa)
7. Pour Location

## Validation
When `--validate` is used, the script checks:
- Missing fields
- Strength values outside 20–100 MPa
- Date format (DD-Mon-YYYY)
- Duplicate cube marks

Validation messages are printed to the console and logged, but output files are still generated so you can review them.

## Logging
Each run creates a `cube_automation.log` file in the output directory for troubleshooting.

## Troubleshooting
- **PDF not found**: confirm the file path is correct
- **No cubes extracted**: check that the PDF contains selectable text and matches the expected report format
- **Empty output sheets**: confirm cube marks include 45D/60D/45DWP/60DWP identifiers

## Project Structure
```
unified_solution/
├── cube_automation.py
├── config.py
├── requirements.txt
├── process_batch.bat
├── modules/
│   ├── pdf_extractor.py
│   ├── excel_writer.py
│   └── data_validator.py
└── templates/
```
