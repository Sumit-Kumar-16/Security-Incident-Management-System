import mysql.connector

def get_db_connection():
    connection =mysql.connector.connect(
        host="localhost",
        user="root",
        password="root@123",
        database="security_incident_db"

    )

    return connection