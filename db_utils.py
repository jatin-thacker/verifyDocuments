# db_utils.py
import os
import pyodbc
from dotenv import load_dotenv
import uuid

load_dotenv()

# Azure SQL connection string
server = os.getenv("AZURE_SQL_SERVER")
database = os.getenv("AZURE_SQL_DATABASE")
username = os.getenv("AZURE_SQL_USERNAME")
password = os.getenv("AZURE_SQL_PASSWORD")

import pyodbc
import time

def get_connection(retries=3, delay=5):
    for attempt in range(retries):
        try:
            conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={os.getenv('SQL_SERVER')};"
                f"DATABASE={os.getenv('SQL_DATABASE')};"
                f"UID={os.getenv('SQL_USERNAME')};"
                f"PWD={os.getenv('SQL_PASSWORD')};"
                "Encrypt=yes;"
                "TrustServerCertificate=yes;"
                "Connection Timeout=30;"
            )
            return conn
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e


def insert_customer_data(data: dict):
    customer_id = str(uuid.uuid4())
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO Customers (CustomerID, FirstName, LastName, DateOfBirth, DocumentNumber, Address, CountryRegion, DateOfExpiration)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (
        customer_id,
        data.get("FirstName"),
        data.get("LastName"),
        data.get("DateOfBirth"),
        data.get("DocumentNumber"),
        data.get("Address"),
        data.get("CountryRegion"),
        data.get("DateOfExpiration"),
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return customer_id
