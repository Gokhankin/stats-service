import os
import pyodbc
from dotenv import load_dotenv

load_dotenv("/home/society/Masaüstü/stats/.env")
CONN_STR = os.getenv("DB_CONNECTION_STRING")
conn = pyodbc.connect(CONN_STR)

EXCLUDED_NAMES = ('aaa', 'TOLA', 'test', 'TEST', 'DUMMY')

query = """
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
  AND ISNULL(r.LastName1, '') NOT IN {0}
  AND ISNULL(r.FirstName1, '') NOT IN {0}
  AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
ORDER BY r.LastName1
""".format(str(EXCLUDED_NAMES))

cursor = conn.cursor()
cursor.execute(query)
rows = cursor.fetchall()
print(f"Total rows: {len(rows)}, Total Pax: {sum(r[4]+r[5] for r in rows)}")
for r in rows:
    print(f"Name: {r[0]} {r[1]} | Agency: {r[3]} | Status: {r[2]} | Pax: {r[4]+r[5]}")

conn.close()
