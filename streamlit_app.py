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
    st.write(f"🧾 DEBUG: Streamlit detected file type: `{uploaded_file.type}`")
    try:
        blob_name = uploaded_file.name
        st.write(f"📎 File name: `{blob_name}`")

        # ✅ Read the bytes first
        image_bytes = uploaded_file.read()

        # ✅ Then upload
        uploaded_file.seek(0)  # rewind for upload
        blob_client = container_client.get_blob_client(blob=blob_name)
        blob_client.upload_blob(uploaded_file, overwrite=True)
        st.success("✅ File uploaded to Azure Blob Storage.")

        # Build SAS URL just for logging
        blob_url = f"{os.getenv('AZURE_BLOB_BASE_URL')}/{blob_name}{sas_token}"
        st.code(f"🔗 SAS URL: {blob_url}", language="text")

        st.info("⏳ Waiting briefly for Azure blob readiness...")
        time.sleep(2)

        st.write("🔍 Extracting data using Azure Document Intelligence...")
        result = extract_id_data(image_bytes=image_bytes, debug=debug_mode)

        if "error" in result:
            st.error(f"❌ Azure Form Recognizer Error:\n\n{result['error']}")
        else:
            st.success("✅ ID Verified Successfully!")
            st.subheader("📋 Extracted Data")
            st.json(result["extracted"])

            if debug_mode and result.get("raw_debug"):
                st.subheader("🔧 Debug Info")
                st.json(result["raw_debug"])

    except Exception as e:
        st.error(f"❌ Upload or analysis failed: {e}")