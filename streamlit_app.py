import streamlit as st
import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from analyze_id import extract_id_data  # or wherever your function is

load_dotenv()

# Load environment variables
container_name = os.getenv("AZURE_BLOB_CONTAINER")
conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
sas_token = os.getenv("SAS_TOKEN")

# Initialize Azure Blob client
blob_service_client = BlobServiceClient.from_connection_string(conn_str)
container_client = blob_service_client.get_container_client(container_name)

st.title("🪪 Smart ID Verification Kiosk")

uploaded_file = st.file_uploader("Upload your ID image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    try:
        # Upload file to Azure Blob Storage
        blob_name = uploaded_file.name
        blob_client = container_client.get_blob_client(blob=blob_name)
        blob_client.upload_blob(uploaded_file, overwrite=True)
        st.code(blob_name, language="text")
        st.code(blob_url, language="text")
        # Construct full SAS URL to access the blob
        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}{sas_token}"

        st.code(blob_url, language="text")
        st.success("✅ File uploaded successfully.")
        st.write("🔍 Extracting data...")

        # Call your Azure Document Intelligence processor
        result = extract_id_data(blob_url)

        if "error" in result:
            st.error(f"❌ {result['error']}")
        else:
            st.success("✅ ID Verified Successfully!")
            st.json(result)

    except Exception as e:
        st.error(f"❌ Upload failed: {e}")
