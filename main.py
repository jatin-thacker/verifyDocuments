import streamlit as st
import requests
import uuid
import sqlite3
import json
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Azure Config
import os
endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

# Init Form Recognizer client
client = DocumentAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

# --- Database setup ---
def init_db():
    conn = sqlite3.connect("smartid.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Customers (
            CustomerID TEXT,
            FirstName TEXT,
            LastName TEXT,
            DateOfBirth TEXT,
            DocumentNumber TEXT,
            Address TEXT,
            CountryRegion TEXT,
            DateOfExpiration TEXT
        )
    """)
    conn.commit()
    conn.close()

def generate_customer_id():
    return str(uuid.uuid4())[:8]

def save_to_db(data: dict):
    customer_id = generate_customer_id()
    conn = sqlite3.connect("smartid.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Customers (
            CustomerID, FirstName, LastName, DateOfBirth, 
            DocumentNumber, Address, CountryRegion, DateOfExpiration
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        customer_id,
        data["FirstName"],
        data["LastName"],
        data["DateOfBirth"],
        data["DocumentNumber"],
        data["Address"],
        data["CountryRegion"],
        data["DateOfExpiration"]
    ))
    conn.commit()
    conn.close()
    return customer_id

def clean_id_data(data: dict) -> dict:
    return {
        "FirstName": data.get("FirstName"),
        "LastName": data.get("LastName"),
        "DateOfBirth": data.get("DateOfBirth"),
        "DocumentNumber": data.get("DocumentNumber"),
        "Address": data.get("Address"),
        "CountryRegion": data.get("CountryRegion") or "US",
        "DateOfExpiration": data.get("DateOfExpiration")
    }

# --- Extract from Azure Form Recognizer ---
def extract_id_data(image_bytes) -> dict:
    poller = client.begin_analyze_document(
        model_id="prebuilt-idDocument",
        document=image_bytes
    )
    result = poller.result()

    fields = {}
    for doc in result.documents:
        for name, field in doc.fields.items():
            fields[name] = field.value if field.value else None
    return fields

# --- Streamlit UI ---
def main():
    st.set_page_config(page_title="Smart ID Kiosk")
    st.title("🪪 Smart ID Kiosk")

    init_db()

    uploaded_file = st.file_uploader("Upload ID Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image_bytes = uploaded_file.read()
        st.image(image_bytes, caption="Uploaded ID", use_column_width=True)

        if st.button("🔍 Process ID"):
            try:
                raw_data = extract_id_data(image_bytes)
                cleaned_data = clean_id_data(raw_data)
                customer_id = save_to_db(cleaned_data)

                st.success("✅ ID Verified and Stored")
                st.write("🆔 Customer ID:", customer_id)

                with st.expander("🔎 Extracted Data"):
                    st.json(cleaned_data)

            except Exception as e:
                st.error(f"❌ Failed to process: {e}")

if __name__ == "__main__":
    main()
