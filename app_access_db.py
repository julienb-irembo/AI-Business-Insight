from pandas import DataFrame
import streamlit as st
import sqlparse
import psycopg2

DB_NAME = st.secrets["DB_NAME"]
DB_USER = st.secrets["DB_USER"]
DB_PASS = st.secrets["DB_PASS"]
DB_HOST = st.secrets["DB_HOST"]
DB_PORT = st.secrets["DB_PORT"]


#check if text is a query with sqlparse
def is_query(text):
    parsed = sqlparse.parse(text)
    if parsed and parsed[0].get_type() == 'SELECT':
        return True
    else:
        return False
    
  
def run_query(query=''):
    try:
        conn = psycopg2.connect(database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT)
        print("Database connected successfully")
    except:
        print("Database not connected successfully")
        
    clean_query = query.replace('```','')
    print(f"clean_query  \n   {clean_query}")
    cursor = conn.cursor()
    cursor.execute(clean_query)     
    print(f"Cursor Description \n   {cursor.description}")

    df = DataFrame(cursor.fetchall())
    print(df.head())
    df.columns = [i[0] for i in cursor.description]

    # print(f'Field Names : {field_names}')
    
    print(df.head())
    conn.close()
    return df
