@echo off
echo Setting up Concrete Cube Report Tool Environment...
echo.

echo Creating conda environment...
conda env create -f environment.yml

echo.
echo Activating environment...
call conda activate concrete-cube-tool

echo.
echo Environment setup complete!
echo To start the application, run: streamlit run app.py
echo.
pause 