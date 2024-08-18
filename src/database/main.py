import streamlit as st
import pymysql

DB_HOST = st.secrets["database"]["DB_HOST"]
DB_PORT = st.secrets["database"]["DB_PORT"]
DB_USERNAME = st.secrets["database"]["DB_USERNAME"]
DB_PASSWORD = st.secrets["database"]["DB_PASSWORD"]
DB_DATABASE = st.secrets["database"]["DB_DATABASE"]
SSL_PATH = st.secrets["database"]["SSL_PATH"]

CONNECTION_STRING = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?ssl_ca={SSL_PATH}&ssl_verify_cert=true&ssl_verify_identity=true'

def create_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        ssl_verify_cert=True,
        ssl_verify_identity=True,
        ssl_ca=SSL_PATH
    )