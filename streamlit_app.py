import streamlit as st
import os
import time
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from analyze_id import extract_id_data  # Make sure this uses bytes, not URL

# Load environment variables
load_dotenv()

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
    st.error(f"❌ Missing environment variables: {', '.join(missing)}")
    st.stop()

# Extract config
conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = os.getenv("AZURE_BLOB_CONTAINER")
base_url = os.getenv("AZURE_BLOB_BASE_URL")
sas_token = os.getenv("SAS_TOKEN")

# Azure blob setup
blob_service_client = BlobServiceClient.from_connection_string(conn_str)
container_client = blob_service_client.get_container_client(container_name)

# Title
st.title("🪪 Smart ID Verification Kiosk")
uploaded_file = st.file_uploader("📤 Upload your ID image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    content_type = uploaded_file.type
    st.write(f"🧾 DEBUG: Streamlit detected file type: `{content_type}`")
    
    image_bytes = uploaded_file.getvalue()
    blob_name = uploaded_file.name

    try:
        st.write(f"📎 File name: `{blob_name}`")

        # Upload to blob
        blob_client = container_client.get_blob_client(blob=blob_name)
        blob_client.upload_blob(image_bytes, overwrite=True)

        st.success("✅ File uploaded to Azure Blob Storage.")
        blob_url = f"{base_url}/{blob_name}{sas_token}"
        st.code(f"🔗 SAS URL: {blob_url}", language="text")

        # Wait a bit to let Azure index the blob
        st.info("⏳ Waiting briefly for Azure blob readiness...")
        time.sleep(2)

        # Extract data
        with st.spinner("🔍 Extracting ID data using Azure AI..."):
            result = extract_id_data(image_bytes=image_bytes, content_type=content_type)

        if "error" in result:
            st.error(f"❌ Azure Form Recognizer Error:\n\n{result['error']}")
        else:
            st.success("✅ ID Verified Successfully!")
            st.json(result)

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
