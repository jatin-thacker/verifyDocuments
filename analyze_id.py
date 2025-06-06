import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

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
        endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
        key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")
        
        poller = client.begin_recognize_id_documents_from_url(sas_url)
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


