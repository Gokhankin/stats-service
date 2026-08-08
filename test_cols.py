import os, pyodbc, pandas as pd
from dotenv import load_dotenv
load_dotenv('/home/society/Masaüstü/stats/.env')
conn_str = os.getenv('DB_CONNECTION_STRING')
conn = pyodbc.connect(conn_str)

q = "SELECT TOP 1 * FROM Agency"
df = pd.read_sql(q, conn)
print("AGENCY COLS:", list(df.columns))
conn.close()
