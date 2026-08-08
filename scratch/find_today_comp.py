import os
import pyodbc
from dotenv import load_dotenv

load_dotenv("/home/society/Masaüstü/stats/.env")
CONN_STR = os.getenv("DB_CONNECTION_STRING")
conn = pyodbc.connect(CONN_STR)

query = """
SELECT 
    r.FirstName1,
    r.LastName1,
    a.AgencyCode,
    r.Pax,
    r.Childs
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE dd.StayDate = '20260520'
  AND dd.Status != -1
  AND r.Status IN (1, 2, 3)
  AND a.AgencyCode LIKE '%COMP%'
"""

cursor = conn.cursor()
cursor.execute(query)
rows = cursor.fetchall()

print("--- TODAY'S COMP GUESTS ---")
for row in rows:
    print(f"Name: {row[0]} {row[1]} | Agency: {row[2]} | Pax: {row[3]} | Childs: {row[4]}")

conn.close()
