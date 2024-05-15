import sqlite3
from pandas import DataFrame
import sqlparse

DB_FILENAME = 'irembo_application_4.db'


#check if text is a query with sqlparse
def is_query(text):
    parsed = sqlparse.parse(text)
    if parsed and parsed[0].get_type() == 'SELECT':
        return True
    else:
        return False
    
    
   


def run_query(query=''):
    
    clean_query = query.replace('```','')
    print(f"clean_query  \n   {clean_query}")
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute(clean_query)     
    #data = cursor.fetchall()
    #print(data)
    #conn.close()
    print(f"Cursor Description \n   {cursor.description}")

    df = DataFrame(cursor.fetchall())
    print(df.head())
    df.columns = [i[0] for i in cursor.description]

    # print(f'Field Names : {field_names}')
    
    print(df.head())
    conn.close()
    return df