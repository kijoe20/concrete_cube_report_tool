# Concrete Cube Test Report Automation Tool

A Streamlit-based web application that automates the extraction and processing of concrete cube test data from PDF reports and generates formatted Excel reports.

## Features

- **PDF Data Extraction**: Automatically extracts concrete cube test data from PDF reports
- **Interactive Data Editor**: Edit and validate extracted data through a user-friendly interface
- **Excel Report Generation**: Creates formatted Excel reports using predefined templates
- **Dynamic Data Handling**: Supports variable number of data rows

## Installation

### Prerequisites

- Python 3.8 or higher
- Conda (recommended) or pip

### Setup with Conda

1. Clone the repository:

```bash
git clone <repository-url>
cd concrete_cube_report_tool
```

2. Create and activate conda environment:

```bash
conda create -n concrete-cube-tool python=3.9
conda activate concrete-cube-tool
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Setup with pip

1. Clone the repository:

```bash
git clone <repository-url>
cd concrete_cube_report_tool
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

## Project Structure

```
concrete_cube_report_tool/
├── app.py                 # Main Streamlit application
├── extract_pdf.py         # PDF data extraction module
├── write_excel.py         # Excel report generation module
├── templates/             # Excel template files
│   └── Concrete-strength-statistic-Superstructure.xlsx
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── .gitignore            # Git ignore rules
```

## Dependencies

- **streamlit**: Web application framework
- **PyMuPDF**: PDF processing and text extraction
- **pandas**: Data manipulation and analysis
- **openpyxl**: Excel file generation and manipulation

## Data Format

The tool extracts the following data fields from PDF reports:

- Cube ID (CU number)
- Cube Mark (prefix, number, suffix)
- Report Number
- Date Cast
- Strength values
- Pour Location

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
