import os
import pyodbc
from dotenv import load_dotenv

load_dotenv("/home/society/Masaüstü/stats/.env")
CONN_STR = os.getenv("DB_CONNECTION_STRING")
conn = pyodbc.connect(CONN_STR)

EXCLUDED_NAMES = ('aaa', 'TOLA', 'test', 'TEST', 'DUMMY')

# Query staying guests for May 20
query_may20 = """
SELECT r.RecId, r.FirstName1, r.LastName1, r.Pax, r.Childs, a.AgencyCode
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE dd.StayDate = '20260520'
  AND dd.Status != -1
  AND r.Status IN (1, 2, 3)
  AND ISNULL(r.LastName1, '') NOT IN {0}
  AND ISNULL(r.FirstName1, '') NOT IN {0}
  AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
""".format(str(EXCLUDED_NAMES))

# Query staying guests for May 21
query_may21 = """
SELECT r.RecId, r.FirstName1, r.LastName1, r.Pax, r.Childs, a.AgencyCode
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE dd.StayDate = '20260521'
  AND dd.Status != -1
  AND r.Status IN (1, 2, 3)
  AND ISNULL(r.LastName1, '') NOT IN {0}
  AND ISNULL(r.FirstName1, '') NOT IN {0}
  AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
""".format(str(EXCLUDED_NAMES))

cursor = conn.cursor()
cursor.execute(query_may20)
guests_20 = {row[0]: (row[1], row[2], row[3] + row[4], row[5]) for row in cursor.fetchall()}

cursor.execute(query_may21)
guests_21 = {row[0]: (row[1], row[2], row[3] + row[4], row[5]) for row in cursor.fetchall()}

# Check-outs: in 20 but not in 21
checkouts = []
for recid, info in guests_20.items():
    if recid not in guests_21:
        checkouts.append(info)

# Check-ins: in 21 but not in 20
checkins = []
for recid, info in guests_21.items():
    if recid not in guests_20:
        checkins.append(info)

print(f"20 May Pax: {sum(x[2] for x in guests_20.values())} ({len(guests_20)} rooms)")
print(f"21 May Pax: {sum(x[2] for x in guests_21.values())} ({len(guests_21)} rooms)")

print("\n--- ACTUAL CHECK-OUTS (20 MAY'DA KALIP 21 MAY'DA KALMAYANLAR) ---")
for x in checkouts:
    print(f"Name: {x[0]} {x[1]} | Pax: {x[2]} | Agency: {x[3]}")

print("\n--- ACTUAL CHECK-INS (21 MAY'DA KALIP 20 MAY'DA KALMAYANLAR) ---")
for x in checkins:
    print(f"Name: {x[0]} {x[1]} | Pax: {x[2]} | Agency: {x[3]}")

conn.close()
