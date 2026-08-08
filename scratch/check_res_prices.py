import os, sys, pyodbc, pandas as pd
from dotenv import load_dotenv
sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
import warnings
warnings.filterwarnings("ignore")

# Let's inspect a few records from Reservation and DailyDetail to understand currency and prices
cursor = conn.cursor()
cursor.execute("""
    SELECT TOP 5 r.RecId, r.RoomPrice, r.DailyRoomPrice, r.DailyRoomLocalPrice, r.Code1, r.Code2, r.Code3,
           r.CheckinDate, r.CheckOutDate, r.Pax, r.Childs
    FROM Reservation r
    WHERE r.CheckinDate BETWEEN '20260501' AND '20260522'
      AND r.Status != -1
""")
for row in cursor.fetchall():
    print("Res:", row)
    
# Let's see if there is a Currency table or a way to get the EUR price
cursor.execute("SELECT TOP 5 * FROM ExchangeRate ORDER BY CurrDate DESC")
for row in cursor.fetchall():
    print("Exchange:", row)
