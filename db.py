import os 
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        port=os.getenv("DB_PORT"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"))


if __name__ == "__main__":
    #not permanent 
    conn = get_connection()
    if conn:
        print("Conexion exitosa\n")
        conn.close()