import os
import sys
import pyodbc
from dotenv import load_dotenv

sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
CONN_STR = os.getenv("DB_CONNECTION_STRING")
conn = pyodbc.connect(CONN_STR)

EXCLUDED_NAMES = ('aaa', 'TOLA', 'test', 'TEST', 'DUMMY')

# Let's query DailyDetail staying guests (Status IN 1, 2, 3) between May 1 and May 20, 2026
# Scenario A: Including COMP, excluding COMP
# Scenario B: All status, only Status 3, etc.

cursor = conn.cursor()

def run_query(label, query):
    cursor.execute(query)
    row = cursor.fetchone()
    print(f"{label}: Rooms = {row[0]}, Pax = {row[1]}")

# 1. Staying guests (StayDate between 1 May and 20 May), status in (1,2,3), excluding COMP
query_no_comp = f"""
SELECT 
    COUNT(DISTINCT dd.RecId) as RoomNights,
    SUM(r.Pax + r.Childs) as PaxNights
FROM DailyDetail dd
LEFT JOIN Reservation r ON r.RecId = dd.ReservationId
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
  AND dd.Status != -1
  AND r.Status IN (1, 2, 3)
  AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
"""
run_query("1. Staying (1,2,3) No COMP", query_no_comp)

# 2. Staying guests (StayDate between 1 May and 20 May), status in (1,2,3), INCLUDING COMP
query_with_comp = f"""
SELECT 
    COUNT(DISTINCT dd.RecId) as RoomNights,
    SUM(r.Pax + r.Childs) as PaxNights
FROM DailyDetail dd
LEFT JOIN Reservation r ON r.RecId = dd.ReservationId
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
  AND dd.Status != -1
  AND r.Status IN (1, 2, 3)
  AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
"""
run_query("2. Staying (1,2,3) With COMP", query_with_comp)

# 3. Staying guests, status in (1,2,3,4) (which is all checked out too) - Wait, dd.StayDate already filters staying days!
# In DailyDetail, dd.Status != -1 means the stay date was stayed.
query_all_statuses_no_comp = f"""
SELECT 
    COUNT(dd.RecId) as RoomNights,
    SUM(r.Pax + r.Childs) as PaxNights
FROM DailyDetail dd
LEFT JOIN Reservation r ON r.RecId = dd.ReservationId
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
  AND dd.Status != -1
  AND r.Status IN (1, 2, 3, 4)
  AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
"""
run_query("3. Staying (1,2,3,4) No COMP (COUNT dd.RecId)", query_all_statuses_no_comp)

query_all_statuses_with_comp = f"""
SELECT 
    COUNT(dd.RecId) as RoomNights,
    SUM(r.Pax + r.Childs) as PaxNights
FROM DailyDetail dd
LEFT JOIN Reservation r ON r.RecId = dd.ReservationId
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
  AND dd.Status != -1
  AND r.Status IN (1, 2, 3, 4)
  AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
"""
run_query("4. Staying (1,2,3,4) With COMP (COUNT dd.RecId)", query_all_statuses_with_comp)

# Let's count by daily query loop
# 5. Let's see how many records in DailyDetail actually exist
query_dd_raw = """
SELECT COUNT(*), SUM(pax) FROM (
    SELECT dd.StayDate, COUNT(dd.RecId) as rooms, SUM(r.Pax + r.Childs) as pax
    FROM DailyDetail dd
    LEFT JOIN Reservation r ON r.RecId = dd.ReservationId
    WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
      AND dd.Status != -1
      AND r.Status IN (1, 2, 3, 4)
      AND ISNULL(r.LastName1, '') NOT IN ('aaa', 'TOLA', 'test', 'TEST', 'DUMMY')
      AND ISNULL(r.FirstName1, '') NOT IN ('aaa', 'TOLA', 'test', 'TEST', 'DUMMY')
    GROUP BY dd.StayDate
) t
"""
cursor.execute(query_dd_raw)
row = cursor.fetchone()
print(f"Raw sum of stay dates: days={row[0]}, pax={row[1]}")

conn.close()
