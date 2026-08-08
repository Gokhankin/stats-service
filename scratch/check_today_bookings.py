import os
import pyodbc
from dotenv import load_dotenv

load_dotenv("/home/society/Masaüstü/stats/.env")
CONN_STR = os.getenv("DB_CONNECTION_STRING")
conn = pyodbc.connect(CONN_STR)

# Find reservations booked today (RecordDate = 2026-05-20)
query = """
SELECT 
    COUNT(r.RecId) as ResCount,
    SUM(r.Pax + r.Childs) as PaxCount,
    COUNT(CASE WHEN r.Status != -1 THEN 1 END) as ActiveResCount,
    SUM(CASE WHEN r.Status != -1 THEN r.Pax + r.Childs ELSE 0 END) as ActivePaxCount
FROM Reservation r
WHERE CAST(r.RecordDate AS DATE) = '2026-05-20'
"""

cursor = conn.cursor()
cursor.execute(query)
row = cursor.fetchone()
print(f"Total entered today: ResCount={row[0]}, PaxCount={row[1]}")
print(f"Active entered today: ResCount={row[2]}, PaxCount={row[3]}")

# Let's also check if they are COMP or not
query_non_comp = """
SELECT 
    COUNT(r.RecId) as ResCount,
    SUM(r.Pax + r.Childs) as PaxCount
FROM Reservation r
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE CAST(r.RecordDate AS DATE) = '2026-05-20'
  AND r.Status != -1
  AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
"""
cursor.execute(query_non_comp)
row_nc = cursor.fetchone()
print(f"Non-COMP entered today: ResCount={row_nc[0]}, PaxCount={row_nc[1]}")

conn.close()
