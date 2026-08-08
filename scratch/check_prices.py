import os, sys, pyodbc, pandas as pd
from dotenv import load_dotenv
sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
import warnings
warnings.filterwarnings("ignore")

cursor = conn.cursor()
cursor.execute("""
    SELECT TOP 5 dd.RecId, dd.StayDate, dd.ReservationId, dd.TotalRoomNetAmount, dd.Status,
           r.RoomPrice, r.DailyRoomPrice, r.DailyRoomLocalPrice, r.StatusCode
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    WHERE dd.StayDate BETWEEN '20260501' AND '20260522'
""")
for row in cursor.fetchall():
    print(row)
