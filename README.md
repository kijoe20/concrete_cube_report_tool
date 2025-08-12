# Concrete Cube Test Report Automation Tool

This project provides two solutions for automating concrete cube test report processing:

## Current Status

**✅ VBA Solution**: Fully functional and ready to use
**🔄 Python Solution**: Fully functional and ready to use  
**🚧 Streamlit Solution**: Under development (new web interface)

## Solutions

### 1. VBA Solution (WORKING - NO FURTHER UPDATES)

A VBA-based solution that processes concrete cube test data directly within Excel using macros and automation.

**Features:**

- **PDF Data Extraction**: Automatically extracts concrete cube test data from PDF reports
- **Interactive Data Editor**: Edit and validate extracted data through Excel interface
- **Excel Report Generation**: Creates formatted Excel reports using predefined templates
- **Dynamic Data Handling**: Supports variable number of data rows

**Status**: This solution is complete and will not receive further updates.

### 2. Python Solution (WORKING)

A Python-based solution that processes concrete cube test data using command-line tools and automation.

**Features:**

- **PDF Data Extraction**: Automatically extracts concrete cube test data from PDF reports
- **Data Processing**: Processes and validates extracted data
- **Excel Report Generation**: Creates formatted Excel reports using predefined templates
- **Batch Processing**: Supports processing multiple files

### 3. Streamlit Solution (UNDER DEVELOPMENT)

A Streamlit-based web application that provides a modern web interface for the concrete cube test automation.

**Features (planned):**

- **Web Interface**: User-friendly web-based interface
- **PDF Data Extraction**: Automatically extracts concrete cube test data from PDF reports
- **Interactive Data Editor**: Edit and validate extracted data through a web interface
- **Excel Report Generation**: Creates formatted Excel reports using predefined templates
- **Dynamic Data Handling**: Supports variable number of data rows

## Installation & Usage

### VBA Solution (Recommended for Excel Users)

1. Navigate to the `VBA_solution/` directory
2. Open `ConcreteCubeReportTemplate.xlsm` in Microsoft Excel
3. Enable macros when prompted
4. Follow the instructions in the VBA solution README

### Python Solution (Recommended for Command Line Users)

1. Navigate to the `python_solution/` directory
2. Follow the installation and usage instructions in the Python solution README

### Streamlit Solution (Under Development)

**Note: This solution is still under development and may not be fully functional.**

1. Navigate to the `streamlit_solution/` directory
2. Follow the installation and usage instructions in the Streamlit solution README

## Project Structure

```
concrete_cube_report_tool/
├── VBA_solution/          # Working VBA solution (no further updates)
│   ├── ConcreteCubeReportTemplate.xlsm
│   ├── modCubeProcessing.bas
│   └── README.md
├── python_solution/       # Working Python solution
│   └── [Python solution files]
├── streamlit_solution/    # Streamlit web app (under development)
│   ├── app.py            # Main Streamlit application
│   ├── extract_pdf_future.py
│   ├── extract_text.py
│   ├── extract_text_1.py
│   ├── write_excel.py
│   ├── templates/        # Excel template files
│   ├── requirements.txt  # Python dependencies
│   ├── environment.yml   # Conda environment file
│   ├── run.bat          # Windows batch file for running Streamlit
│   └── setup.bat        # Windows batch file for setup
├── README.md            # Project documentation
└── .gitignore          # Git ignore rules
```

## Dependencies

### VBA Solution

- Microsoft Excel with VBA support enabled
- No additional dependencies required

### Python Solution

- Python 3.8 or higher
- Required packages listed in `python_solution/requirements.txt`

### Streamlit Solution (Under Development)

- Python 3.8 or higher
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
