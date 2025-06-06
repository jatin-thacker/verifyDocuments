import streamlit as st
import os
import time
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

import os
import streamlit as st

required_envs = [
    "AZURE_FORM_RECOGNIZER_ENDPOINT",
    "AZURE_FORM_RECOGNIZER_KEY",
    "AZURE_STORAGE_CONNECTION_STRING",
    "AZURE_BLOB_CONTAINER",
    "AZURE_BLOB_BASE_URL",
    "SAS_TOKEN"
]

missing = [var for var in required_envs if not os.getenv(var)]
if missing:
    st.error(f"Missing required environment variables: {', '.join(missing)}")
    st.stop()
    
st.title("🪪 Smart ID Verification Kiosk")

uploaded_file = st.file_uploader("📤 Upload your ID image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    blob_url = None  # Initialize to avoid undefined reference
    try:
        # Define blob name and upload to Azure
        blob_name = uploaded_file.name
        st.write(f"📎 File name: `{blob_name}`")

        blob_client = container_client.get_blob_client(blob=blob_name)
        blob_client.upload_blob(uploaded_file, overwrite=True)
        st.success("✅ File uploaded to Azure Blob Storage.")
        st.code(f"📦 Container: {container_name}", language="text")
        st.code(f"🔑 SAS Token: {sas_token}", language="text")

        # Give Azure some time to register the new blob (Azure can be slow to propagate)
        st.info("⏳ Waiting for blob availability...")
        time.sleep(3)  # 3 seconds delay

        # Build SAS URL
        blob_url = f"{os.getenv('AZURE_BLOB_BASE_URL')}/{blob_name}{sas_token}"
        st.code(f"🔗 SAS URL: {blob_url}", language="text")

        st.write("🔍 Extracting data using Azure Document Intelligence...")

        result = extract_id_data(blob_url)  # 👈 use the real uploaded file's URL

        if "error" in result:
            st.error(f"❌ Azure Form Recognizer Error: {result['error']}")
        else:
            st.success("✅ ID Verified Successfully!!!")
            st.json(result)

    except Exception as e:
        st.error(f"❌ Upload failed: {e}")
        if not blob_url:
            st.warning("ℹ️ Blob URL was never created. Upload may have failed...")
