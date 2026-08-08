import os, sys, pyodbc, pandas as pd
from dotenv import load_dotenv
sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
import warnings
warnings.filterwarnings("ignore")

cursor = conn.cursor()
cursor.execute("SELECT * FROM DailyDetail WHERE ReservationId = 25661")
row = cursor.fetchone()
cols = [col[0] for col in cursor.description]
for c, val in zip(cols, row):
    if val is not None and val != 0 and val != '':
        print(f"{c}: {val}")
