# Streamlit Solution - Concrete Cube Test Report Automation

**Status: Under Development**

This is a Streamlit-based web application that provides a modern web interface for the concrete cube test automation tool.

## Features (Planned)

- **Web Interface**: User-friendly web-based interface
- **PDF Data Extraction**: Automatically extracts concrete cube test data from PDF reports
- **Interactive Data Editor**: Edit and validate extracted data through a web interface
- **Excel Report Generation**: Creates formatted Excel reports using predefined templates
- **Dynamic Data Handling**: Supports variable number of data rows

## Prerequisites

- Python 3.8 or higher
- Conda (recommended) or pip

## Installation

### Setup with Conda (Recommended)

1. Navigate to the `streamlit_solution/` directory:

```bash
cd streamlit_solution
```

2. Create and activate conda environment:

```bash
conda create -n concrete-cube-streamlit python=3.9
conda activate concrete-cube-streamlit
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Setup with pip

1. Navigate to the `streamlit_solution/` directory:

```bash
cd streamlit_solution
```

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Windows Quick Setup

1. Double-click `setup.bat` to automatically set up the environment
2. Double-click `run.bat` to start the application

## Usage

1. Start the Streamlit application:

```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided URL (usually `http://localhost:8501`)

3. Upload a PDF report containing concrete cube test data

4. Review and edit the extracted data in the interactive data editor

5. Click "Generate Excel Report" to create the formatted Excel file

6. Download the generated Excel report

## Dependencies

- **streamlit**: Web application framework
- **PyMuPDF**: PDF processing and text extraction
- **pandas**: Data manipulation and analysis
- **openpyxl**: Excel file generation and manipulation

## Project Structure

```
streamlit_solution/
├── app.py                 # Main Streamlit application
├── extract_pdf_future.py  # PDF data extraction module
├── extract_text.py        # PDF text extraction utilities
├── extract_text_1.py      # Additional PDF text extraction utilities
├── write_excel.py         # Excel report generation module
├── templates/             # Excel template files
│   └── Concrete-strength-statistic-Superstructure.xlsx
├── requirements.txt       # Python dependencies
├── environment.yml        # Conda environment file
├── run.bat               # Windows batch file for running Streamlit
├── setup.bat             # Windows batch file for setup
└── README.md             # This file
```

## Development Status

This solution is currently under development. Features may not be fully functional.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.