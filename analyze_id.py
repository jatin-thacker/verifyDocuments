from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

if not endpoint or not key:
    raise ValueError("AZURE_FORM_RECOGNIZER_ENDPOINT or AZURE_FORM_RECOGNIZER_KEY not set in environment.")

client = FormRecognizerClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

def extract_id_data(image_bytes: bytes, content_type: str):
    print("DEBUG: extract_id_data called with image_bytes and content_type:", content_type)
    
    try:
        print("DEBUG: Starting Azure Document Intelligence analysis...")
        poller = client.begin_recognize_identity_documents(
            identity_document=image_bytes,
            content_type=content_type
        )
        result = poller.result()

        if not result or len(result) == 0:
            print("DEBUG: No documents returned by recognizer.")
            return {"error": "No documents returned by Azure Form Recognizer."}

        id_document = result[0]
        print(f"DEBUG: Document Type Detected: {id_document.doc_type}")

        # Extract core fields
        extracted = {
            "FirstName": id_document.first_name.content if id_document.first_name else None,
            "LastName": id_document.last_name.content if id_document.last_name else None,
            "FullName": id_document.full_name.content if id_document.full_name else None,
            "DocumentNumber": id_document.document_number.content if id_document.document_number else None,
            "DateOfBirth": id_document.date_of_birth.content if id_document.date_of_birth else None,
            "IssueDate": id_document.date_of_issue.content if id_document.date_of_issue else None,
            "ExpirationDate": id_document.date_of_expiration.content if id_document.date_of_expiration else None,
            "Sex": id_document.sex.content if id_document.sex else None,
            "Address": id_document.address.content if id_document.address else None,
            "City": id_document.city.content if id_document.city else None,
            "Province": id_document.state.content if id_document.state else None,
            "PostalCode": id_document.postal_code.content if id_document.postal_code else None,
            "Country": id_document.country_region.content if id_document.country_region else None,
        }

        print("DEBUG: Extracted Key Fields:")
        for k, v in extracted.items():
            print(f"  {k}: {v}")

        # Optional: print all fields with confidence for debugging
        print("\nDEBUG: Raw Fields with Confidence:")
        raw_fields = {}
        for field_name in [
            "first_name", "last_name", "full_name", "document_number", "date_of_birth", "date_of_issue",
            "date_of_expiration", "sex", "address", "city", "state", "postal_code", "country_region"
        ]:
            field = getattr(id_document, field_name, None)
            if field:
                raw_fields[field_name] = {
                    "value": field.content if hasattr(field, "content") else str(field.value),
                    "confidence": round(field.confidence, 2) if hasattr(field, "confidence") else "N/A"
                }
        print(raw_fields)

        return extracted

    except Exception as e:
        print(f"ERROR: Exception during Form Recognizer call: {e}")
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


