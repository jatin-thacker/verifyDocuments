import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

def extract_id_data(sas_url: str) -> dict:
    from azure.ai.formrecognizer import DocumentAnalysisClient
    from azure.core.credentials import AzureKeyCredential
    import os

    endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
    key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

    client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    try:
        poller = client.begin_analyze_document_from_url("prebuilt-idDocument", document_url=sas_url)
        result = poller.result()

        extracted_data = {}
        for doc in result.documents:
            for name, field in doc.fields.items():
                extracted_data[name] = field.value

        return extracted_data
    except Exception as e:
        return {"error": str(e)}


