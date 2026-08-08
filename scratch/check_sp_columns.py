import os, sys, pyodbc, pandas as pd
from dotenv import load_dotenv

sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))

import warnings
warnings.filterwarnings("ignore")

sql = "SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='20260522', @AvailableRoom=0"
df = pd.read_sql(sql, conn)
print("--- Columns ---")
for col in df.columns:
    if 'room' in col.lower() or 'rev' in col.lower() or 'acc' in col.lower() or 'konaklama' in col.lower():
        print(col)
        
print("--- Values ---")
row = df.iloc[0]
for col in df.columns:
    if 'room' in col.lower() or 'rev' in col.lower() or 'acc' in col.lower():
        val = row[col]
        if pd.notna(val) and isinstance(val, (int, float)) and val > 0:
            print(f"{col}: {val}")
