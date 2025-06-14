import streamlit as st
import os
import time
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from analyze_id import extract_id_data  # Make sure this function takes a SAS URL
from db_utils import insert_customer_data
from db_utils import get_connection

load_dotenv()


# Validate environment variables
required_envs = [
    "AZURE_STORAGE_CONNECTION_STRING",
    "AZURE_BLOB_CONTAINER",
    "AZURE_BLOB_BASE_URL",
    "SAS_TOKEN"
]
missing = [var for var in required_envs if not os.getenv(var)]
if missing:
    st.error(f"Missing required environment variables: {', '.join(missing)}")
    st.stop()

# Load env vars
conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = os.getenv("AZURE_BLOB_CONTAINER")
sas_token = os.getenv("SAS_TOKEN")

# Azure Blob setup
blob_service_client = BlobServiceClient.from_connection_string(conn_str)
container_client = blob_service_client.get_container_client(container_name)

st.set_page_config(page_title="Smart ID Verification Kiosk", layout="centered")
st.title("🪪 Smart ID Verification Kiosk")

if st.button("🔌 Test DB Connection"):
    try:
        conn = get_connection()
        st.success("✅ Connected to DB successfully!")
        conn.close()
    except Exception as e:
        st.error(f"❌ DB Connection Failed: {e}")


uploaded_file = st.file_uploader("📤 Upload your ID image", type=["jpg", "jpeg", "png"])
debug_mode = st.checkbox("🔍 Enable debug info (raw values & confidence)")

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
            customer_id = insert_customer_data(result["extracted"])
            st.success(f"🎉 Onboarding Complete! Your Customer ID is: `{customer_id}`")

            if debug_mode and result.get("raw_debug"):
                st.subheader("🔧 Debug Info")
                st.json(result["raw_debug"])

    except Exception as e:
        st.error(f"❌ Upload or analysis failed: {e}")