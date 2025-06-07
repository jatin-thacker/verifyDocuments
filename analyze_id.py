import os
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import requests 

# Keep this line if you plan to test analyze_id.py standalone, otherwise remove
# import streamlit as st 

load_dotenv()

endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

if not endpoint or not key:
    print("ERROR: Azure Document Intelligence endpoint or key not found in environment variables.")
    raise ValueError("Environment variables AZURE_FORM_RECOGNIZER_ENDPOINT and AZURE_FORM_RECOGNIZER_KEY must be set.")

client = FormRecognizerClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )

# MODIFIED: content_type is directly passed and we will trust it completely
def extract_id_data(sas_url: str, content_type: str): 
    print(f"DEBUG: extract_id_data called with SAS URL: {sas_url}, PASSED Content-Type: {content_type}")
    print("DEBUG: Starting document analysis with FormRecognizerClient...")
    
    extracted = {}

    try:
        response = requests.get(sas_url)
        response.raise_for_status() 
        
        image_data = response.content 
        
        # --- CRITICAL: We are now explicitly trusting the `content_type`
        # --- that was passed directly from streamlit_app.py.
        # --- All previous inference/fallback logic for content_type is REMOVED.
        print(f"DEBUG: Using FINAL Content-Type for analysis: {content_type}") 

        poller = client.begin_recognize_identity_documents(
            identity_document=image_data, 
            content_type=content_type # Directly use the passed content_type
        )
        result = poller.result()
        
        print(f"DEBUG: AnalyzeResult object received: {result}")

        if not result: 
            print("DEBUG: No identity documents found in the image or no results returned from Azure.")
            return {"error": "No ID documents found in the image or no results returned from Azure."}

        id_document = result[0] 
        
        print(f"DEBUG: Found identity document type: {id_document.doc_type}")

        extracted = {
            "FirstName": id_document.first_name.content if id_document.first_name else None,
            "LastName": id_document.last_name.content if id_document.last_name else None,
            "DocumentNumber": id_document.document_number.content if id_document.document_number else None,
            "DateOfBirth": id_document.date_of_birth.content if id_document.date_of_birth else None,
            "Address": id_document.address.content if id_document.address else None,
            "City": id_document.city.content if id_document.city else None,
            "Province": id_document.state.content if id_document.state else None, 
            "PostalCode": id_document.postal_code.content if id_document.postal_code else None,
            "Country": id_document.country_region.content if id_document.country_region else None, 
            "Sex": id_document.sex.content if id_document.sex else None,
            "ExpirationDate": id_document.date_of_expiration.content if id_document.date_of_expiration else None, 
            "IssueDate": id_document.date_of_issue.content if id_document.date_of_issue else None, 
            "FullName": id_document.full_name.content if id_document.full_name else None, 
        }
        
        print("\n--- Extracted Data (Key-Value Pairs) ---")
        print(extracted)
        print("----------------------------------------")
        
        print("\n--- All Raw IdentityDocument Attributes (for Debugging) ---")
        all_raw_fields_dict = {}
        for attr_name in ['document_number', 'date_of_birth', 'date_of_expiration', 'date_of_issue',
                          'first_name', 'last_name', 'full_name', 'address', 'city', 'state',
                          'postal_code', 'country_region', 'sex', 'first_name_native',
                          'last_name_native', 'document_subtype', 'issuing_authority', 'nationality',
                          'place_of_birth', 'region', 'visa_number', 'machine_readable_zone']:
            
            field_value_obj = getattr(id_document, attr_name, None)
            if field_value_obj:
                content_or_value = field_value_obj.content if hasattr(field_value_obj, 'content') else field_value_obj.value
                
                if isinstance(content_or_value, (type(None))):
                    display_value = None
                elif hasattr(content_or_value, 'isoformat'):
                    display_value = content_or_value.isoformat()
                else:
                    display_value = str(content_or_value)

                confidence = field_value_obj.confidence if hasattr(field_value_obj, 'confidence') else 'N/A'
                all_raw_fields_dict[attr_name] = {
                    "content_or_value": display_value,
                    "confidence": f"{confidence:.2f}" if isinstance(confidence, float) else confidence
                }
        print(all_raw_fields_dict)
        print("--------------------------------------------------")

        return extracted

    except requests.exceptions.HTTPError as err:
        print(f"ERROR: HTTP Error during image download: {err}")
        print(f"DEBUG: Response headers from requests.get (failed download): {response.headers}") # NEW DEBUG LINE
        return {"error": f"Failed to download image from SAS URL: {err}"}
    except Exception as e:
        print(f"ERROR: Azure AI Form Recognizer Error: {e}") 
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


