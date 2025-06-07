import os
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import streamlit as st  # Optional for testing/debugging

load_dotenv()

endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

if not endpoint or not key:
    raise ValueError("Missing environment variables: AZURE_FORM_RECOGNIZER_ENDPOINT and/or AZURE_FORM_RECOGNIZER_KEY")

client = FormRecognizerClient(endpoint=endpoint, credential=AzureKeyCredential(key))


def extract_id_data(image_bytes: bytes, content_type: str) -> dict:
    print("🧠 DEBUG: Starting Azure Form Recognizer with bytes input...")
    extracted = {}

    try:
        poller = client.begin_recognize_identity_documents(
            identity_document=image_bytes,
            content_type=content_type
        )
        result = poller.result()

        if not result:
            return {"error": "No identity documents were detected in the image."}

        doc = result[0]

        extracted = {
            "FirstName": doc.first_name.content if doc.first_name else None,
            "LastName": doc.last_name.content if doc.last_name else None,
            "FullName": doc.full_name.content if doc.full_name else None,
            "DocumentNumber": doc.document_number.content if doc.document_number else None,
            "DateOfBirth": doc.date_of_birth.content if doc.date_of_birth else None,
            "ExpirationDate": doc.date_of_expiration.content if doc.date_of_expiration else None,
            "IssueDate": doc.date_of_issue.content if doc.date_of_issue else None,
            "Address": doc.address.content if doc.address else None,
            "City": doc.city.content if doc.city else None,
            "Province": doc.state.content if doc.state else None,
            "PostalCode": doc.postal_code.content if doc.postal_code else None,
            "Country": doc.country_region.content if doc.country_region else None,
            "Sex": doc.sex.content if doc.sex else None,
        }

        return extracted

    except Exception as e:
        print(f"❌ ERROR during ID extraction: {e}")
        return {"error": str(e)}



# import os
# from azure.ai.formrecognizer import DocumentAnalysisClient
# from azure.core.credentials import AzureKeyCredential
# from dotenv import load_dotenv
# import requests

# load_dotenv()
# # Setup Form Recognizer Client
# endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
# key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

# client = DocumentAnalysisClient(
#             endpoint=endpoint,
#             credential=AzureKeyCredential(key)
#         )

# def extract_id_data(sas_url: str):

#     try:
#         print(f"DEBUG: extract_id_data called with SAS URL: {sas_url}")
#         print("DEBUG: Starting document analysis...")
#         #endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
#         #key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")
#         #image_url = r"https://smartidstorage123.blob.core.windows.net/ids/test1.jpg?sp=r&st=2025-06-05T20:02:28Z&se=2025-06-19T04:02:28Z&sv=2024-11-04&sr=c&sig=5e%2F%2BoCFrwEOBY0UlhNzvwABtc63AWAfHodI%2FAGYzHmY%3D"
#         #image_data = requests.get(image_url).content
#         #poller = client.begin_recognize_id_documents_from_url(sas_url)
#         #poller = client.begin_analyze_document("prebuilt-idDocument", url_source=sas_url)
#         #poller = client.begin_analyze_document("prebuilt-idDocument", image_data)

#         image_data = requests.get(sas_url).content
#         poller = client.begin_analyze_document(
#             "prebuilt-idDocument",
#             document=image_data # <<< Pass the raw bytes
#         )
#         result = poller.result()
#         extracted = {}
#         print(f"DEBUG: AnalyzeResult object received: {result}")
#         if not result:
#             return {"error": "No results returned from Azure."}

#         # Just return the raw fields to see what we get
#         #fields = result[0].fields if result else {}
#         # st.write("Raw fields:", fields)
#         #fields = result.documents[0].fields
#         # extracted = {
#         # "FirstName": fields.get("FirstName").value if fields.get("FirstName") else None,
#         # "LastName": fields.get("LastName").value if fields.get("LastName") else None,
#         # "DateOfBirth": fields.get("DateOfBirth").value if fields.get("DateOfBirth") else None,
#         # "DocumentNumber": fields.get("DocumentNumber").value if fields.get("DocumentNumber") else None,
#         # }

#         if result.documents:
#             doc = result.documents[0]

#             print(f"DEBUG: Found document type: {doc.doc_type}")
#             #st.success(f"Document analysis complete. Type: {doc.doc_type}")

#             # Access fields using dot notation and .get() for safety
#             fields = doc.fields

#         # Create the 'extracted_data' dictionary
#             extracted = {
#                 "FirstName": fields.get("FirstName").content if fields.get("FirstName") else None,
#                 "LastName": fields.get("LastName").content if fields.get("LastName") else None,
#                 # If your model might return "FullName" directly, include it
#                 "FullName": fields.get("FullName").content if fields.get("FullName") else None,
#                 "DateOfBirth": fields.get("DateOfBirth").content if fields.get("DateOfBirth") else None,
#                 "DocumentNumber": fields.get("DocumentNumber").content if fields.get("DocumentNumber") else None,
#                 # Add any other fields you need here, e.g., "Address", "ExpirationDate", etc.
#                 # Example:
#                 # "ExpirationDate": fields.get("ExpirationDate").value.isoformat() if fields.get("ExpirationDate") and fields.get("ExpirationDate").value else None,
#             }

        
#         print(fields)

#         return extracted or {"error": "No fields extracted."}

#     except Exception as e:
#         return {"error": str(e)}

