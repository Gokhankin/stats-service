import os
import sys
import pyodbc
import pandas as pd
from dotenv import load_dotenv

sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
CONN_STR = os.getenv("DB_CONNECTION_STRING")
conn = pyodbc.connect(CONN_STR)

cursor = conn.cursor()
sql = "SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='20260520', @AvailableRoom=0"
df = pd.read_sql(sql, conn)

print("Columns matching 1462 or near values:")
for col in df.columns:
    val = df[col].iloc[0]
    if isinstance(val, (int, float)) and abs(val - 1462) < 20:
        print(f"{col}: {val}")

print("\nAll fields containing 'Pax' or 'Room' or 'Night' in Monthly/Yearly:")
for col in df.columns:
    if any(x in col for x in ['Pax', 'Room', 'Night']) and any(y in col for y in ['Monthly', 'Yearly']):
        val = df[col].iloc[0]
        print(f"{col}: {val}")

conn.close()
