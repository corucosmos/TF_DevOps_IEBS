import mysql.connector
from mysql.connector import Error
import os

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            #host=os.getenv('MYSQL_HOST', 'mysql'),
            #user=os.getenv('MYSQL_USER', 'user'),
            #password=os.getenv('MYSQL_PASSWORD', 'password'),
            #database=os.getenv('MYSQL_DB', 'userdb')
            host = os.getenv("DB_HOST"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_NAME")

        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None