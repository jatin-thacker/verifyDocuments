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
    server = os.getenv("AZURE_SQL_SERVER")
    database = os.getenv("AZURE_SQL_DATABASE")
    username = os.getenv("AZURE_SQL_USERNAME")
    password = os.getenv("AZURE_SQL_PASSWORD")
    print(f"[DEBUG] Values are: server is  {server} , database is : {database}, username is : {username}, and the password is {password}.")
    for attempt in range(retries):
        try:
            conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                "Encrypt=yes;"
                "TrustServerCertificate=yes;"
                "Connection Timeout=30;"
            )
            print("[DEBUG] Connection succeeded")
            return conn
        except Exception as e:
            print(f"[DEBUG] Connection attempt {attempt + 1} failed: {e}")
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
