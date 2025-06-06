import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()


def extract_id_data(sas_url):
	
    endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
    key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")
    sas_url = os.getenv("AZURE_SAS_URL")

    client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
	
    poller = client.begin_analyze_document_from_url(
	    model_id="prebuilt-idDocument",
	    document_url=sas_url 
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

