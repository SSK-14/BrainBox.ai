import streamlit as st
import pymysql
import json

DB_HOST = st.secrets["database"]["DB_HOST"]
DB_PORT = st.secrets["database"]["DB_PORT"]
DB_USERNAME = st.secrets["database"]["DB_USERNAME"]
DB_PASSWORD = st.secrets["database"]["DB_PASSWORD"]
DB_DATABASE = st.secrets["database"]["DB_DATABASE"]

def create_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        ssl_verify_cert = True,
        ssl_verify_identity = True,
        ssl_ca = "/etc/ssl/cert.pem"
    )

def create_table():
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS studies (
        id INT PRIMARY KEY AUTO_INCREMENT,
        title VARCHAR(255) NOT NULL,
        results JSON,
        summary TEXT,
        type VARCHAR(255) NOT NULL
    )
    """
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_sql)
            connection.commit()
    finally:
        connection.close()

def insert_study_data(data):
    insert_sql = """
    INSERT INTO studies (title, results, summary, type)
    VALUES (%s, %s, %s, %s)
    """
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(insert_sql, (
                data['title'],
                json.dumps(data['results']),
                data['summary'],
                data['type']
            ))
            connection.commit()
            last_id = cursor.lastrowid
            return last_id
    except Exception as e:
        st.error(f"An error occurred: {e}")
        connection.rollback()
    finally:
        connection.close()

def fetch_all_studies():
    fetch_sql = "SELECT * FROM studies"
    connection = create_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(fetch_sql)
            studies = cursor.fetchall()
            return studies
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []
    finally:
        connection.close()

create_table()