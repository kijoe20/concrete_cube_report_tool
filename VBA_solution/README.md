# 🧱 Concrete Cube Report Formatter (.xlsm)

This Excel tool automates formatting for monthly concrete cube test reports. It organizes data by concrete strength type, sorts by date and cube number, and merges relevant cells for clean reporting.

## Features

✅ Split data into 45D, 60D, 45DWP, and 60DWP sheets  
✅ Merge cells with same location or cube number  
✅ One-click processing via VBA macro  
✅ Sample CSV input included

## How to Use

1. Open `ConcreteCubeReportTemplate.xlsm`
2. Paste raw data into the `"Raw"` sheet
3. Press `Alt + F8` → Run `RunAllProcessingSteps`
4. Check formatted output in respective sheets

## Folder Structure

- `modCubeProcessing.bas`: Importable VBA module
- `README.md`: Project overview

## License
MIT
