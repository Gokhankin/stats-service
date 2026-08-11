import os
import pyodbc
from dotenv import load_dotenv
from queries import get_pace_analysis

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

conn_str = os.getenv('CONN_STR')
conn = pyodbc.connect(conn_str)

res = get_pace_analysis(conn, "08-11")
print("Pace Analysis Results:")
for r in res:
    print(r)

conn.close()
