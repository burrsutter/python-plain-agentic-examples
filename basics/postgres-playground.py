import psycopg2
from psycopg2 import sql

contact_to_find = "%elizabeth%"

try:
    # Establish a connection to the PostgreSQL database
    connection = psycopg2.connect(
        dbname="northwind",
        user="postgres",
        password="admin",
        host="localhost",
        port="5432"
    )

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # version query
    cursor.execute("SELECT version();")    

    # Fetch and display the result of the query
    db_version = cursor.fetchone()
    print(f"Version - {db_version}")

    # Execute a query to retrieve the list of databases
    cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")

    # Fetch all database names
    databases = cursor.fetchall()

    # Display the list of databases
    print("List of databases:")
    for db in databases:
        print(f"- {db[0]}")

    # Execute a query to retrieve the list of tables in the 'public' schema
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)    
    
    # Fetch all table names
    tables = cursor.fetchall()

    # Display the list of tables
    print("List of tables in the database:")
    for table in tables:
        print(f"- {table[0]}")


    # Execute a query to retrieve all customers
    cursor.execute("SELECT customer_id, company_name, contact_name FROM customers LIMIT 5;")

    # Fetch all customer records
    customers = cursor.fetchall()

    # Display the list of customers
    print("List of customers:")
    for customer in customers:
        print(customer)

    # find customers by contact name match
    print("Find contacts", contact_to_find)

    query = sql.SQL("""
        SELECT customer_id, company_name, contact_name
        FROM customers
        WHERE contact_name ILIKE %s
    """)

    # Execute the query with the search pattern as a parameter
    cursor.execute(query, (contact_to_find,))

    # Fetch all matching records
    customers = cursor.fetchall()

    # Display the list of customers
    print("Customers with 'elizabeth' in their contact name:")
    for customer in customers:
        print(f"ID: {customer[0]}, Company: {customer[1]}, Contact Name: {customer[2]}")
    

except Exception as error:
    print(f"Error connecting to PostgreSQL database: {error}")

finally:
    # Close the cursor and connection to clean up
    if cursor:
        cursor.close()
    if connection:
        connection.close()