import streamlit as st
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from database import insert_customer_data
from PIL import Image
import io
import uuid
import os

endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")
client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

st.title("🪪 Smart ID Kiosk - US ID Only")

uploaded_file = st.file_uploader("Upload your ID", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    image_bytes = uploaded_file.read()

    with st.spinner("Analyzing ID..."):
        try:
            poller = client.begin_analyze_document("prebuilt-idDocument", document=image_bytes)
            result = poller.result()

            fields = result.documents[0].fields

            data = {
                "FirstName": fields.get("FirstName").value if fields.get("FirstName") else None,
                "LastName": fields.get("LastName").value if fields.get("LastName") else None,
                "DateOfBirth": fields.get("DateOfBirth").value if fields.get("DateOfBirth") else None,
                "DocumentNumber": fields.get("DocumentNumber").value if fields.get("DocumentNumber") else None,
                "Address": fields.get("Address").value if fields.get("Address") else None,
                "DateOfExpiration": fields.get("DateOfExpiration").value if fields.get("DateOfExpiration") else None,
                "CountryRegion": fields.get("CountryRegion").value if fields.get("CountryRegion") else "US",
            }

            #customer_id = str(uuid.uuid4())
            #insert_customer_data(customer_id, data)

            st.success("✅ ID Processed Successfully")
            #st.json({**{"CustomerID": customer_id}, **data})

        except Exception as e:
            st.error(f"❌ Failed to process: {str(e)}")
