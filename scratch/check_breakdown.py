import os
import sys
import pyodbc
from dotenv import load_dotenv

sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
CONN_STR = os.getenv("DB_CONNECTION_STRING")
conn = pyodbc.connect(CONN_STR)

cursor = conn.cursor()

# We want to find which reservation statuses or agency exclusions yield around 1462.
# Let's group by r.Status to see what we get for May 1-20, 2026.
print("--- GROUPED BY RESERVATION STATUS (StayDate 1-20 May 2026) ---")
q1 = """
SELECT 
    r.Status,
    COUNT(dd.RecId) as RoomNights,
    SUM(r.Pax + r.Childs) as PaxNights
FROM DailyDetail dd
LEFT JOIN Reservation r ON r.RecId = dd.ReservationId
WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
  AND dd.Status != -1
GROUP BY r.Status
"""
cursor.execute(q1)
for row in cursor.fetchall():
    print(f"Status: {row[0]} | RoomNights: {row[1]} | PaxNights: {row[2]}")

print("\n--- GROUPED BY AGENCY (StayDate 1-20 May 2026) ---")
q2 = """
SELECT TOP 15
    a.AgencyCode,
    COUNT(dd.RecId) as RoomNights,
    SUM(r.Pax + r.Childs) as PaxNights
FROM DailyDetail dd
LEFT JOIN Reservation r ON r.RecId = dd.ReservationId
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
  AND dd.Status != -1
GROUP BY a.AgencyCode
ORDER BY PaxNights DESC
"""
cursor.execute(q2)
for row in cursor.fetchall():
    print(f"Agency: {row[0]} | RoomNights: {row[1]} | PaxNights: {row[2]}")

print("\n--- CHECKING INHOUSE STATUS (dd.Status = 3 vs others) ---")
# dd.Status is the daily status: 1:Conf, 2:Block, 3:Inhouse, etc.
# Let's group by dd.Status
q3 = """
SELECT 
    dd.Status,
    COUNT(dd.RecId) as RoomNights,
    SUM(r.Pax + r.Childs) as PaxNights
FROM DailyDetail dd
LEFT JOIN Reservation r ON r.RecId = dd.ReservationId
WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
GROUP BY dd.Status
"""
cursor.execute(q3)
for row in cursor.fetchall():
    print(f"DailyDetail dd.Status: {row[0]} | RoomNights: {row[1]} | PaxNights: {row[2]}")

print("\n--- CHECKING RESERVATION VOUCHER / AGENCY TYPE OR OTHER COMBINATIONS ---")
# Could 1462 be room nights including/excluding Neilson?
# Neilson actual bookings for May 1-20:
q_neilson = """
SELECT 
    COUNT(dd.RecId) as RoomNights,
    SUM(r.Pax + r.Childs) as PaxNights
FROM DailyDetail dd
LEFT JOIN Reservation r ON r.RecId = dd.ReservationId
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
  AND dd.Status != -1
  AND a.AgencyCode LIKE '%NEILSON%'
"""
cursor.execute(q_neilson)
row = cursor.fetchone()
print(f"Neilson: RoomNights = {row[0]}, PaxNights = {row[1]}")

conn.close()
