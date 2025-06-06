import streamlit as st
import os
from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv
from analyze_id import extract_id_data
from verify_and_route import verify_data
import uuid

load_dotenv()


# Safe environment variable fetch
def get_env_var(key: str):
    value = os.getenv(key)
    if value is None:
        st.error(f"❌ Environment variable '{key}' is not set.")
    return value or ""

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_BLOB_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER")

st.title("🆔 Smart ID Kiosk System")

uploaded_file = st.file_uploader("📄 Upload your ID Document", type=["jpg", "png", "jpeg", "pdf"])

if uploaded_file is not None:
    st.info(f"Filename: {uploaded_file.name}")
    if st.button("📤 Upload and Analyze"):
        try:
            blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
            blob_client = blob_service_client.get_blob_client(
                container=AZURE_BLOB_CONTAINER,
                blob=f"{uuid.uuid4()}_{uploaded_file.name}"
            )

            # Upload the file
            blob_client.upload_blob(
                uploaded_file,
                overwrite=True,
                content_settings=ContentSettings(content_type=uploaded_file.type)
            )

            # Generate SAS URL for Azure Document Intelligence
            sas_url = blob_client.url + os.getenv("SAS_TOKEN")  # from .env

            st.success("✅ File uploaded successfully.")
            #st.write("🔗 SAS URL:", sas_url)
            st.write("🔗 SAS URL:", r"C:\Users\jatin\Downloads\smart-id-kiosk\smart-id-kiosk\test1.jpg")
            with st.spinner("Analyzing document..."):
                data = extract_id_data(sas_url)

            if not data:
                st.error("❌ Failed to extract data.")
            else:
                st.success("✅ Data extracted successfully:")
                st.json(data)

                verified, msg = verify_data(data)
                if verified:
                    st.success("✅ Verification Passed. Profile created.")
                else:
                    st.warning("⚠️ Verification Failed. Routed to underwriter.")

        except Exception as e:
            st.error(f"Upload failed: {e}")
