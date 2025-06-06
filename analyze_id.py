import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import requests

load_dotenv()
# Setup Form Recognizer Client
endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )

def extract_id_data(sas_url: str):
    try:
        #endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
        #key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")
        image_url = r"https://smartidstorage123.blob.core.windows.net/ids/test1.jpg?sp=r&st=2025-06-05T20:02:28Z&se=2025-06-19T04:02:28Z&sv=2024-11-04&sr=c&sig=5e%2F%2BoCFrwEOBY0UlhNzvwABtc63AWAfHodI%2FAGYzHmY%3D"
        image_data = requests.get(image_url).content
        #poller = client.begin_recognize_id_documents_from_url(sas_url)
        #poller = client.begin_analyze_document("prebuilt-idDocument", sas_url)
        poller = client.begin_analyze_document("prebuilt-idDocument", document=image_data)
        result = poller.result()

        if not result:
            return {"error": "No results returned from Azure."}

        # Just return the raw fields to see what we get
        fields = result[0].fields if result else {}
        # st.write("Raw fields:", fields)
        fields = result.documents[0].fields
        extracted = {
        "FirstName": fields.get("FirstName").value if fields.get("FirstName") else None,
        "LastName": fields.get("LastName").value if fields.get("LastName") else None,
        "DateOfBirth": fields.get("DateOfBirth").value if fields.get("DateOfBirth") else None,
        "DocumentNumber": fields.get("DocumentNumber").value if fields.get("DocumentNumber") else None,
        }


        return extracted or {"error": "No fields extracted."}

    except Exception as e:
        return {"error": str(e)}


