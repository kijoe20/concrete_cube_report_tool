@echo off
echo Starting Concrete Cube Report Tool...
echo.

call conda activate concrete-cube-tool
streamlit run app.py

pause 