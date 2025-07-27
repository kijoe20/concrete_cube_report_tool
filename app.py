import streamlit as st
from extract_pdf_future import extract_cube_data
from extract_text import extract_cube_data_from_text
from extract_text_1 import extract_from_text
from write_excel import write_to_excel
import pandas as pd
from io import BytesIO

st.title("Concrete Cube Test Report Automation Tool")

# Mode selection
mode = st.radio("Choose input method", ["Paste Text", "Upload PDF (WIP)", "Alternative Text Parser"])

if mode == "Upload PDF (WIP)":
    st.warning("PDF upload is under development.")
    uploaded_pdf = st.file_uploader("Upload PDF Report", type=["pdf"])
    if uploaded_pdf:
        st.write("### Processing PDF...")
        cube_data, raw_blocks = extract_cube_data(uploaded_pdf)
        
        if cube_data:
            df = pd.DataFrame(cube_data)
            st.write(f"### Extracted Data ({len(df)} rows)")
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

            if st.button("Generate Excel Report"):
                output = BytesIO()
                write_to_excel(edited_df, output)
                st.success("Excel generated!")
                st.download_button("Download Excel", output.getvalue(), "cube_report.xlsx")
        else:
            st.error("No data could be extracted from the PDF. Please check the file format and try again.")
            st.write("### Troubleshooting Tips:")
            st.write("1. Make sure the PDF contains concrete cube test data")
            st.write("2. Check that the PDF is not password protected")
            st.write("3. Ensure the PDF contains text (not just images)")
            st.write("4. Verify the data format matches expected patterns (CU numbers, dates, etc.)")

elif mode == "Alternative Text Parser":
    # Alternative text input mode using extract_text_1.py
    st.write("### Alternative Text Parser")
    st.info("Use the alternative parsing method for PDF content. Copy and paste the text content from your PDF report below.")
    
    pasted_text = st.text_area("Paste PDF content here", height=300, 
                               placeholder="Paste the text content from your PDF report here...")
    
    if pasted_text:
        st.write("### Processing Text with Alternative Parser...")
        cube_data = extract_from_text(pasted_text)
        
        if cube_data:
            df = pd.DataFrame(cube_data)
            st.write(f"### Extracted Data ({len(df)} rows)")
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
            
            if st.button("Generate Excel Report"):
                output = BytesIO()
                write_to_excel(edited_df, output)
                st.success("Excel generated!")
                st.download_button("Download Excel", output.getvalue(), "cube_report.xlsx")
        else:
            st.error("No data could be extracted from the text. Please check the format and try again.")
    else:
        st.info("Please paste the PDF content above to begin processing.")

else:
    # Text input mode
    st.write("### Paste PDF Content")
    st.info("Copy and paste the text content from your PDF report below.")
    
    pasted_text = st.text_area("Paste PDF content here", height=300, 
                               placeholder="Paste the text content from your PDF report here...")
    
    if pasted_text:
        st.write("### Processing Text...")
        cube_data = extract_cube_data_from_text(pasted_text)
        
        if cube_data:
            df = pd.DataFrame(cube_data)
            st.write(f"### Extracted Data ({len(df)} rows)")
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
            
            if st.button("Generate Excel Report"):
                output = BytesIO()
                write_to_excel(edited_df, output)
                st.success("Excel generated!")
                st.download_button("Download Excel", output.getvalue(), "cube_report.xlsx")
        else:
            st.error("No data could be extracted from the text. Please check the format and try again.")
    else:
        st.info("Please paste the PDF content above to begin processing.")


