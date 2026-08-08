import os, sys, pyodbc, pandas as pd
from dotenv import load_dotenv
sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
import warnings
warnings.filterwarnings("ignore")

# Let's inspect the columns of DailyDetail
cursor = conn.cursor()
cursor.execute("SELECT TOP 1 * FROM DailyDetail")
columns = [col[0] for col in cursor.description]
print("DailyDetail columns:", columns)

# Also let's inspect Reservation columns
cursor.execute("SELECT TOP 1 * FROM Reservation")
r_columns = [col[0] for col in cursor.description]
print("Reservation columns:", r_columns)
