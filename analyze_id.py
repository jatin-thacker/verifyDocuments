import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

def extract_id_data(sas_url):
    endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
    key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    poller = document_analysis_client.begin_analyze_document_from_url(
        "prebuilt-idDocument", sas_url
    )
    result = poller.result()

    if not result.documents:
        return None

    fields = result.documents[0].fields
    extracted = {
        "FullName": fields.get("FirstName").value if fields.get("FirstName") else None
	,"LastName": fields.get("LastName").value if fields.get("LastName") else None
        ,"DateOfBirth": fields.get("DateOfBirth").value if fields.get("DateOfBirth") else None
        #,"CountryRegion": fields.get("CountryRegion").value if fields.get("CountryRegion") else None
        ,"DocumentNumber": fields.get("DocumentNumber").value if fields.get("DocumentNumber") else None
    }
    return extracted

