@echo off
echo Concrete Cube Report Batch Processor
echo ====================================
echo.

set /p INPUT_FOLDER="Enter PDF folder path: "
set /p OUTPUT_FOLDER="Enter output folder path: "

python -m unified_solution "%INPUT_FOLDER%" --folder --output-dir "%OUTPUT_FOLDER%" --validate

pause
