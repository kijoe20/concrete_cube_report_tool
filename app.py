import streamlit as st
from extract_pdf import extract_cube_data
from write_excel import write_to_excel
import pandas as pd
from io import BytesIO

st.title("Concrete Cube Test Report Automation Tool")

uploaded_pdf = st.file_uploader("Upload PDF Report", type=["pdf"])
if uploaded_pdf:
    cube_data, raw_blocks = extract_cube_data(uploaded_pdf)
    df = pd.DataFrame(cube_data)
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    if st.button("Generate Excel Report"):
        output = BytesIO()
        write_to_excel(edited_df, output)
        st.success("Excel generated!")
        st.download_button("Download Excel", output.getvalue(), "cube_report.xlsx")
