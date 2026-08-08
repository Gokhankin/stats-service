import os, sys, pyodbc, pandas as pd
from dotenv import load_dotenv
sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
import warnings
warnings.filterwarnings("ignore")

cursor = conn.cursor()
cursor.execute("SELECT DefaultDate, Count(*) FROM DefaultDate WHERE CompanyRecId=1 AND DefaultDate BETWEEN '20260501' AND '20260522' GROUP BY DefaultDate HAVING Count(*) > 1")
rows = cursor.fetchall()
if rows:
    for r in rows:
        print("Duplicate DefaultDate:", r)
else:
    print("No duplicates in DefaultDate table")
