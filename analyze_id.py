import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

def extract_id_data(sas_url: str):
    try:
        poller = client.begin_recognize_id_documents_from_url(sas_url)
        result = poller.result()

        if not result:
            return {"error": "No results returned from Azure."}

        # Just return the raw fields to see what we get
        fields = result[0].fields if result else {}

        # Convert to readable dictionary
        extracted = {}
        for key, field in fields.items():
            extracted[key] = field.value if field else None

        return extracted or {"error": "No fields extracted."}

    except Exception as e:
        return {"error": str(e)}


