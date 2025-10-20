# Concrete Cube Test Report PDF Extractor

## Overview
This Python automation tool extracts concrete cube test data from PDF reports and converts it to a structured CSV format.

## Output Format
The program generates a pipe-delimited (|) CSV file with the following columns:
1. **Cube Mark Prefix** (e.g., "20250621-45D-", "20250622-45DWP-")
2. **Cube Number** (e.g., "1", "11")
3. **Cube Suffix** (e.g., "A", "B")
4. **Report Number** (e.g., "04428CU763515")
5. **Date Cast** (e.g., "02-Jul-2025")
6. **Compressive Strength** in MPa (e.g., "82.6")
7. **Pour Location** (e.g., "23/F-25/F Zone 2 Column and Wall at G.L. T-17 to T-33 & T-Q to T-F")

## Requirements
- Python 3.7+
- pdfplumber library

## Installation

### Install Dependencies
```bash
pip install pdfplumber
```

Or using requirements.txt:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python cube_extractor.py <input_pdf> <output_csv>
```

### Example
```bash
python cube_extractor.py Prelim-202507.pdf output.csv
```

### Command Line Arguments
- `input_pdf`: Path to the input PDF report
- `output_csv`: Path where the output CSV will be saved

## How It Works

### 1. Cube Mark Parsing
The program automatically splits cube marks into three components:
- **Prefix**: Date and concrete type (e.g., "20250621-45D-")
- **Number**: Cube sequence number (e.g., "1", "11")
- **Suffix**: Cube variant letter (e.g., "A", "B")

Example parsing:
- Input: `20250621-45D-1A`
- Output: Prefix=`20250621-45D-`, Number=`1`, Suffix=`A`

### 2. Data Extraction
For each page in the PDF, the program extracts:
- **Report Number**: From "Report No.: XXXXX" field
- **Date Cast**: From "Date Cast: DD-Mon-YYYY" field
- **Pour Location**: From "Location:" or "Pour Location:" field
- **Cube Data**: All cube marks and their compressive strengths

### 3. CSV Generation
The extracted data is written to a CSV file with pipe (|) delimiters, one row per cube.

## Output Example
```
20250702-60D-|1|A|04428CU763515|02-Jul-2025|82.6|23/F-25/F Zone 2 Column and Wall at G.L. T-17 to T-33 & T-Q to T-F
20250702-60D-|1|B|04428CU763515|02-Jul-2025|79.5|23/F-25/F Zone 2 Column and Wall at G.L. T-17 to T-33 & T-Q to T-F
20250702-60D-|2|A|04428CU763515|02-Jul-2025|81.8|23/F-25/F Zone 2 Column and Wall at G.L. T-17 to T-33 & T-Q to T-F
```

## Features
- Automatic cube mark parsing and splitting
- Handles multiple cube types (45D, 60D, 45DWP, etc.)
- Extracts page-level metadata (report number, date, location)
- Robust text extraction from PDF pages
- Clean, structured CSV output
- No header row (data only)

## Error Handling
- Validates command line arguments
- Checks for file existence
- Provides clear error messages
- Graceful handling of missing data fields

## Limitations
- Requires pdfplumber for PDF text extraction
- Assumes standard report format
- Text-based PDF extraction (not image-based)

## Troubleshooting

### Module Not Found Error
```bash
pip install pdfplumber
```

### PDF Not Found
Ensure the PDF file path is correct and the file exists.

### Empty Output
Check that the PDF contains extractable text and follows the expected format.

## File Structure
```
.
├── cube_extractor.py      # Main extraction script
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── example_output.csv     # Sample output
```

## License
This tool is provided as-is for concrete testing data management.
