import os
from azure.ai.documentintelligence import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import requests # Still needed for downloading content

# Ensure these imports are at the very top of your Streamlit app file if they are used there
import streamlit as st

load_dotenv()

# --- Initialize client (outside the function, as you correctly have it) ---
# This part should be at the top level of your Streamlit app script
endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

if not endpoint or not key:
    print("ERROR: Azure Document Intelligence endpoint or key not found in environment variables.")
    # In a Streamlit app, you might also use st.error and st.stop() here
    # st.error("Azure Document Intelligence endpoint or key not found in environment variables.")
    # st.stop()
    raise ValueError("Environment variables AZURE_FORM_RECOGNIZER_ENDPOINT and AZURE_FORM_RECOGNIZER_KEY must be set.")

client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
# --- End client initialization ---


def extract_id_data(sas_url: str):
    print(f"DEBUG: extract_id_data called with SAS URL: {sas_url}")
    print("DEBUG: Starting document analysis...")
    
    extracted = {} # Initialize dictionary for returned data

    try:
        # --- Download content with error checking and get headers ---
        response = requests.get(sas_url)
        response.raise_for_status() # This will raise an HTTPError for bad responses (4xx or 5xx)
        
        image_data = response.content # Get the raw bytes of the image
        content_type = response.headers.get("Content-Type") # Get the Content-Type from the HTTP response headers

        if not content_type:
            # Fallback if Content-Type header is missing (shouldn't happen often for blobs)
            print("WARNING: Content-Type header not found. Attempting to infer from URL.")
            if sas_url.lower().endswith((".jpg", ".jpeg")):
                content_type = "image/jpeg"
            elif sas_url.lower().endswith(".png"):
                content_type = "image/png"
            elif sas_url.lower().endswith(".pdf"):
                content_type = "application/pdf"
            else:
                # If still unknown, log an error and let the service try to guess (might fail)
                print("ERROR: Could not reliably determine content type from URL. This might lead to issues.")
                content_type = "application/octet-stream" # Generic binary type, might fail

        print(f"DEBUG: Determined Content-Type for analysis: {content_type}")

        # --- Call Document Intelligence with explicit content_type ---
        poller = client.begin_analyze_document(
            "prebuilt-idDocument",
            document=image_data,
            content_type=content_type # <<< PASS THE EXPLICIT CONTENT TYPE HERE
        )
        result = poller.result()
        
        print(f"DEBUG: AnalyzeResult object receivedsss: {result}")

        if not result or not result.documents:
            print("DEBUG: No documents or analysis result found.")
            return {"error": "No ID documents found in the image or no results returned from Azure."}

        # If we reach here, we have at least one document
        doc = result.documents[0]
        
        print(f"DEBUG: Found document type: {doc.doc_type}")

        fields = doc.fields

        # Populate the 'extracted' dictionary with fields you care about
        extracted = {
            "FirstName": fields.get("FirstName").content if fields.get("FirstName") else None,
            "LastName": fields.get("LastName").content if fields.get("LastName") else None,
            "FullName": fields.get("FullName").content if fields.get("FullName") else None,
            "DateOfBirth": fields.get("DateOfBirth").content if fields.get("DateOfBirth") else None,
            "DocumentNumber": fields.get("DocumentNumber").content if fields.get("DocumentNumber") else None,
            "Address": fields.get("Address").content if fields.get("Address") else None,
            "City": fields.get("City").content if fields.get("City") else None,
            "Province": fields.get("Province").content if fields.get("Province") else None,
            "PostalCode": fields.get("PostalCode").content if fields.get("PostalCode") else None,
            "Country": fields.get("Country").content if fields.get("Country") else None,
            "Sex": fields.get("Sex").content if fields.get("Sex") else None,
            "ExpirationDate": fields.get("ExpirationDate").content if fields.get("ExpirationDate") else None, # Use .content
            "IssueDate": fields.get("DateOfIssue").content if fields.get("DateOfIssue") else None, # Use .content
            # Add other relevant fields for Canadian IDs
        }
        
        # --- Print the extracted data to the console for debugging ---
        print("\n--- Extracted Data (Key-Value Pairs) ---")
        print(extracted)
        print("----------------------------------------")
        
        # --- Also print all raw fields for detailed debugging ---
        print("\n--- All Raw Fields Extracted (for Debugging) ---")
        all_raw_fields_dict = {}
        for field_name, field_value in fields.items():
            # Try to get content, fallback to value if content is None (e.g., for dates which might have .value)
            content_or_value = field_value.content if field_value.content is not None else field_value.value
            # For date objects, .value might be a datetime object; convert to string for print
            if isinstance(content_or_value, (type(None))):
                display_value = None
            elif hasattr(content_or_value, 'isoformat'): # for datetime objects
                display_value = content_or_value.isoformat()
            else:
                display_value = str(content_or_value)

            confidence = field_value.confidence
            all_raw_fields_dict[field_name] = {
                "content_or_value": display_value,
                "confidence": f"{confidence:.2f}"
            }
        print(all_raw_fields_dict)
        print("--------------------------------------------------")

        return extracted # This will return the dictionary to your Streamlit app

    except requests.exceptions.HTTPError as err:
        print(f"ERROR: HTTP Error during image download: {err}")
        return {"error": f"Failed to download image from SAS URL: {err}"}
    except Exception as e:
        print(f"ERROR: Azure AI Document Intelligence Error: {e}")
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


