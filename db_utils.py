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

def get_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};DATABASE={database};UID={username};PWD={password};"
        f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60;"
    )
    return pyodbc.connect(conn_str)

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
