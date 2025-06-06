import streamlit as st
import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from analyze_id import extract_id_data  # Make sure this function takes a SAS URL

load_dotenv()

# Load env variables
container_name = os.getenv("AZURE_BLOB_CONTAINER")
conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
sas_token = os.getenv("SAS_TOKEN")

# Initialize Azure blob client
blob_service_client = BlobServiceClient.from_connection_string(conn_str)
container_client = blob_service_client.get_container_client(container_name)

st.title("🪪 Smart ID Verification Kiosk")

uploaded_file = st.file_uploader("📤 Upload your ID image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    blob_url = None  # Initialize to avoid undefined reference
    try:
        # Define blob name and upload to Azure
        blob_name = uploaded_file.name
        blob_client = container_client.get_blob_client(blob=blob_name)
        blob_client.upload_blob(uploaded_file, overwrite=True)

        # Build SAS URL
        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}{sas_token}"

        st.success("✅ File uploaded successfully.")
        st.code(blob_url, language="text")

        st.write("🔍 Extracting data...")
        result = extract_id_data(blob_url)  # 👈 use the real uploaded file's URL

        if "error" in result:
            st.error(f"❌ {result['error']}")
        else:
            st.success("✅ ID Verified Successfully!")
            st.json(result)

    except Exception as e:
        st.error(f"❌ Upload failed: {e}")
        if not blob_url:
            st.warning("ℹ️ Blob URL was never created. Upload may have failed.")
