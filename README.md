# Concrete Cube Test Report Automation Tool

This repository contains multiple workflows for extracting concrete cube test
data from PDF reports and generating formatted Excel workbooks. Choose the
approach that best fits your tooling (Excel/VBA, command line, or web UI).

## Solution overview

| Solution | Purpose | Status | Directory |
| --- | --- | --- | --- |
| Unified Python | End-to-end PDF to Excel with validation and batch mode | Stable, recommended | `unified_solution/` |
| PDF to CSV extractor | Extracts pipe-delimited cube data for custom pipelines | Stable | `pdf2csv/` |
| Python Excel processor | Formats an existing Raw worksheet into 45D/60D sheets | Stable | `python_solution/` |
| VBA Excel macro | Formats data inside an Excel template | Stable, no further updates | `VBA_solution/` |
| Streamlit web app | Web UI for extraction and report generation | Under development | `streamlit_solution/` |

## Recommended workflow (Unified Python solution)

1. Install dependencies:
   ```bash
   cd unified_solution
   pip install -r requirements.txt
   ```
2. Run a single PDF:
   ```bash
   python -m unified_solution input.pdf output.xlsx
   ```
3. Optional: batch processing with validation:
   ```bash
   python -m unified_solution ./pdfs/ --folder --output-dir ./reports --validate
   ```

## Other workflows

### VBA solution (Excel users)
1. Open `VBA_solution/ConcreteCubeReportTemplate.xlsm` in Excel.
2. Enable macros and run the `RunAllProcessingSteps` macro.
3. See `VBA_solution/README.md` for details.

### PDF to CSV extractor
1. Install dependencies in `pdf2csv/`.
2. Run `python cube_extractor.py <input_pdf> <output_csv>`.
3. See `pdf2csv/README.md` for output format details.

### Python Excel processor
1. Place an input workbook named `cube_data.xlsx` (with a `Raw` sheet) next to `cube_processing.py`.
2. Run `python cube_processing.py`.
3. See `python_solution/README.md` for requirements and behavior.

### Streamlit web app (under development)
Follow setup and usage instructions in `streamlit_solution/README.md`.

## Project structure

```
.
├── pdf2csv/
│   ├── cube_extractor.py
│   ├── quick_debug.py
│   ├── example_output.csv
│   ├── requirements.txt
│   └── README.md
├── python_solution/
│   ├── cube_processing.py
│   ├── requirements.txt
│   └── README.md
├── streamlit_solution/
│   ├── app.py
│   ├── extract_pdf_future.py
│   ├── extract_text.py
│   ├── extract_text_1.py
│   ├── write_excel.py
│   ├── requirements.txt
│   ├── environment.yml
│   ├── run.bat
│   ├── setup.bat
│   └── README.md
├── unified_solution/
│   ├── __main__.py
│   ├── cube_automation.py
│   ├── config.py
│   ├── requirements.txt
│   ├── process_batch.bat
│   ├── modules/
│   ├── templates/
│   └── README.md
├── VBA_solution/
│   ├── ConcreteCubeReportTemplate.xlsm
│   ├── modCubeProcessing.bas
│   └── README.md
└── README.md
```

## Dependencies

- Python 3.8+ is recommended for the Python-based tools.
- Each solution has its own `requirements.txt` or environment file. Refer to the
  README in the corresponding directory.

## Data format (common fields)

Most workflows extract or emit the following fields:

- Cube mark (prefix, number, suffix)
- Report number
- Date cast
- Compressive strength
- Pour location

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test thoroughly.
5. Submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for
details.
