import os
import pyodbc
from dotenv import load_dotenv

load_dotenv("/home/society/Masaüstü/stats/.env")
CONN_STR = os.getenv("DB_CONNECTION_STRING")
conn = pyodbc.connect(CONN_STR)

EXCLUDED_NAMES = ('aaa', 'TOLA', 'test', 'TEST', 'DUMMY')

# Status: 1 = Confirmed, 2 = Block, 3 = InHouse
query = f"""
SELECT 
    r.FirstName1,
    r.LastName1,
    r.Status,
    a.AgencyCode,
    r.Pax,
    r.Childs
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE dd.StayDate = '20260520'
  AND dd.Status != -1
  AND r.Status IN (1, 2, 3)
  AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
ORDER BY r.Status DESC, r.LastName1
"""

cursor = conn.cursor()
cursor.execute(query)
rows = cursor.fetchall()

status_map = {1: "Confirmed (Beklenen)", 2: "Block", 3: "Inhouse (Otelde)"}

print("TOTAL_COUNT:", len(rows))
print("TOTAL_PAX:", sum(row[4] + row[5] for row in rows))

for idx, row in enumerate(rows, 1):
    status_str = status_map.get(row[2], f"Status {row[2]}")
    name = f"{row[0]} {row[1]}".strip()
    print(f"{idx:02d}. {name:<30} | {status_str:<20} | Agency: {row[3]:<10} | Pax: {row[4]} | Childs: {row[5]}")

conn.close()
