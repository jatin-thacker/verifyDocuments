import streamlit as st
from analyze_id import extract_id_data
from verify_and_route import verify_data
import os
from dotenv import load_dotenv

load_dotenv()

st.title("🆔 Smart ID Kiosk System")

sas_url = st.text_input("🔗 Paste Azure Blob SAS URL of your ID image")

if st.button("📤 Analyze ID"):
    if sas_url:
        with st.spinner("Analyzing document..."):
            data = extract_id_data(sas_url)

        if not data:
            st.error("Failed to extract data. Please check your SAS URL or try again.")
        else:
            st.success("✅ Data extracted successfully:")
            st.json(data)

            verified, message = verify_data(data)
            if verified:
                st.success("✅ Verification Passed. Profile created.")
            else:
                st.warning("⚠️ Verification Failed. Routed to underwriter.")
    else:
        st.warning("Please enter a valid SAS URL.")
