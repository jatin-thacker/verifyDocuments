import sqlite3

def insert_customer_data(customer_id, data):
    conn = sqlite3.connect("customers.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS customers (
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
    c.execute("""
        INSERT INTO customers (
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
