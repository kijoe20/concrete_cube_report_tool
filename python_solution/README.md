# Cube Processing Python Solution

This Python solution processes Excel cube test data by splitting it into different concrete types and applying cell merging operations.

## Overview

The script replicates VBA functionality to:
1. Split raw cube data into separate worksheets based on concrete type (45D, 60D, 45DWP, 60DWP)
2. Merge cells in pour location column (G) when consecutive values are the same
3. Merge every two rows in columns A and B for better formatting

## Requirements

- Python 3.7+
- openpyxl library

## Installation

1. Install the required dependency:
```bash
pip install -r requirements.txt
```

Or install directly:
```bash
pip install openpyxl>=3.1.2
```

## Usage

1. Place your input Excel file named `cube_data.xlsx` in the same directory as the script
2. Run the script:
```bash
python cube_processing.py
```

3. The processed file will be saved as `cube_data_processed.xlsx`

## Input File Requirements

- Must contain a worksheet named "Raw" with cube test data
- Column A should contain concrete type markers (e.g., "45D", "60DWP", etc.)
- Column G should contain pour location data
- First row should contain headers

## Functions

### `get_strict_type(mark: str) -> str`
Determines the concrete type based on the mark string:
- Returns "45DWP" for marks containing both "45D" and "WP"
- Returns "60DWP" for marks containing both "60D" and "WP"  
- Returns "45D" for marks containing "45D"
- Returns "60D" for marks containing "60D"
- Returns "Unknown" for unrecognized marks

### `create_or_clear(ws_name: str, wb) -> Worksheet`
Creates a new worksheet or clears an existing one while preserving the worksheet structure.

### `split_by_type(wb)`
Main function that:
1. Creates target worksheets for each concrete type
2. Copies headers from the Raw worksheet
3. Distributes data rows to appropriate worksheets based on concrete type

### `merge_pour_locations(ws: Worksheet, col_letter: str = "G")`
Merges consecutive cells with the same value in the pour location column and centers the text vertically.

### `merge_every_two(ws: Worksheet, col_letter: str)`
Merges every two consecutive rows in the specified column and centers the text vertically.

### `run_all()`
Main execution function that orchestrates the entire processing workflow.

## Output

The script creates four separate worksheets in the output file:
- **45D**: Regular 45-day concrete test data
- **60D**: Regular 60-day concrete test data  
- **45DWP**: 45-day waterproof concrete test data
- **60DWP**: 60-day waterproof concrete test data

Each worksheet includes:
- Merged cells in column G for consecutive pour locations
- Merged every two rows in columns A and B
- Properly formatted and centered cell alignment

## File Structure

```
python_solution/
├── cube_processing.py    # Main processing script
├── requirements.txt      # Python dependencies
├── README.md            # This documentation
├── cube_data.xlsx       # Input file (place your data here)
└── cube_data_processed.xlsx  # Output file (generated after running)
```

## Notes

- The script preserves the original VBA logic for concrete type classification
- Cell merging is applied automatically based on data patterns
- The input file name is currently hardcoded as "cube_data.xlsx"
- The output file name is hardcoded as "cube_data_processed.xlsx"

## Troubleshooting

- Ensure the input file exists and contains a "Raw" worksheet
- Check that column A contains recognizable concrete type markers
- Verify that the openpyxl library is properly installed
- Make sure the input file is not open in Excel when running the script