import os
import logging
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import requests

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmartIDLogger")

# Load credentials
endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

if not endpoint or not key:
    raise ValueError("Environment variables AZURE_FORM_RECOGNIZER_ENDPOINT and AZURE_FORM_RECOGNIZER_KEY must be set.")

client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))


def extract_id_data(image_bytes: bytes, debug=False):
    logger.info("Starting extract_id_data with image bytes.")
    extracted = {}
    raw_fields = {}

    try:
        logger.debug(f"Sending bytes to Form Recognizer...")
        poller = client.begin_analyze_document(
            model_id="prebuilt-idDocument",
            document=image_bytes
        )
        result = poller.result()
        logger.info("Received response from Azure Form Recognizer.")

        if not result.documents:
            logger.warning("No identity documents detected in the image.")
            return {"error": "No identity documents were detected in the image."}


        doc = result.documents[0]
        fields = doc.fields
        logger.info(f"Document type: {doc.doc_type}")

        # Extract specific fields
        extracted = {
            "FirstName": fields.get("FirstName").content if fields.get("FirstName") else None,
            "LastName": fields.get("LastName").content if fields.get("LastName") else None,
            #"FullName": fields.get("FullName").content if fields.get("FullName") else None,
            "DateOfBirth": fields.get("DateOfBirth").content if fields.get("DateOfBirth") else None,
            "DocumentNumber": fields.get("DocumentNumber").content if fields.get("DocumentNumber") else None,
            "Address": fields.get("Address").content if fields.get("Address") else None,
            #"CountryRegion": fields.get("CountryRegion").content if fields.get("CountryRegion") else "USA",
            "Country": fields.get("Address").content if fields.get("Address") and fields.get("Address").content else "USA",
            "DateOfExpiration": fields.get("DateOfExpiration").content if fields.get("DateOfExpiration") else None,
        }

        if debug:
            for key, field in fields.items():
                if field:
                    raw_fields[key] = {
                        "content": getattr(field, "content", None),
                        "value": getattr(field, "value", None),
                        "confidence": f"{getattr(field, 'confidence', 'N/A'):.2f}" if isinstance(getattr(field, 'confidence', None), float) else "N/A"
                    }

        return {"extracted": extracted, "raw_debug": raw_fields if debug else None}

    except Exception as e:
        logger.exception("Error in extract_id_data.")
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

