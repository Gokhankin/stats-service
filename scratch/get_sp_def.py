import os, sys, pyodbc
from dotenv import load_dotenv
sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))

cursor = conn.cursor()
cursor.execute("SELECT definition FROM sys.sql_modules WHERE object_id = OBJECT_ID('ManagerReport')")
row = cursor.fetchone()
if row:
    # Print first 2000 chars or write to a scratch file
    with open("/home/society/Masaüstü/stats/scratch/manager_report_def.sql", "w") as f:
        f.write(row[0])
    print("Stored procedure definition written to manager_report_def.sql")
else:
    print("Stored procedure definition not found")
