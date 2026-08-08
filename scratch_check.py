import pyodbc, os
from dotenv import load_dotenv
load_dotenv()
conn = pyodbc.connect(os.getenv('DB_CONNECTION_STRING'), timeout=10)
cursor = conn.cursor()

# VipTypeCode
cursor.execute("SELECT DISTINCT VipTypeCode, COUNT(*) as cnt FROM Reservation WHERE YEAR(CheckinDate) IN (2025,2026) AND Status IN (1,2,3,4) GROUP BY VipTypeCode ORDER BY cnt DESC")
print('=== VIP TYPE CODES ===')
for row in cursor.fetchall():
    print(row)

# ForecastType
cursor.execute("SELECT DISTINCT ForecastType, COUNT(*) as cnt FROM Reservation WHERE YEAR(CheckinDate) IN (2025,2026) AND Status IN (1,2,3,4) GROUP BY ForecastType ORDER BY cnt DESC")
print('\n=== FORECAST TYPES ===')
for row in cursor.fetchall():
    print(row)

# PriceType
cursor.execute("SELECT DISTINCT PriceType, COUNT(*) as cnt FROM Reservation WHERE YEAR(CheckinDate) IN (2025,2026) AND Status IN (1,2,3,4) GROUP BY PriceType ORDER BY cnt DESC")
print('\n=== PRICE TYPES ===')
for row in cursor.fetchall():
    print(row)

# Comp/Staff sample - look for 0 price reservations
cursor.execute("SELECT TOP 10 LastName1, FirstName1, PriceType, VipTypeCode, ForecastType, DailyRoomPrice, Board FROM Reservation WHERE YEAR(CheckinDate) IN (2025,2026) AND Status IN (1,2,3,4) AND ISNULL(DailyRoomPrice,0) = 0")
print('\n=== ZERO PRICE RESERVATIONS (possible comp/staff) ===')
for row in cursor.fetchall():
    print(row)

conn.close()
