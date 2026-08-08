import os
import sys
import pyodbc
from dotenv import load_dotenv

sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
CONN_STR = os.getenv("DB_CONNECTION_STRING")
conn = pyodbc.connect(CONN_STR)
cursor = conn.cursor()

print("=== ATTEMPT 1: ManagerReport 'Monthly' Room-Night style fields ===")
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
sql = "SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='20260520', @AvailableRoom=0"
df = pd.read_sql(sql, conn)
# Print all Monthly/Yearly fields that could be room/pax counts (integers not ratios)
for col in df.columns:
    val = df[col].iloc[0]
    if isinstance(val, (int, float)) and 1400 <= val <= 1550:
        print(f"  {col}: {val}")

print("\n=== ATTEMPT 2: Direct DailyPax table query ===")
# Maybe 1462 comes from the DailyPax table (a pre-aggregated table)
try:
    cursor.execute("""
        SELECT TOP 5 COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'DailyPax'
    """)
    cols = cursor.fetchall()
    print("DailyPax columns:", [c[0] for c in cols])
    cursor.execute("""
        SELECT * FROM DailyPax 
        WHERE StayDate BETWEEN '20260501' AND '20260520'
    """)
    rows = cursor.fetchall()
    print(f"DailyPax rows for May 1-20: {len(rows)}")
    for r in rows[:5]:
        print(r)
except Exception as e:
    print(f"DailyPax error: {e}")

print("\n=== ATTEMPT 3: Sedna's 'StatisticsView' or Summary tables ===")
try:
    cursor.execute("""
        SELECT TOP 3 TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE' 
        AND (TABLE_NAME LIKE '%Stat%' OR TABLE_NAME LIKE '%Summary%' OR TABLE_NAME LIKE '%Report%' OR TABLE_NAME LIKE '%Night%')
        ORDER BY TABLE_NAME
    """)
    tables = cursor.fetchall()
    print("Related tables:", [t[0] for t in tables])
except Exception as e:
    print(f"Tables error: {e}")

print("\n=== ATTEMPT 4: DailyDetail with dd.Status=1 only (Confirmed StayDates) ===")
# dd.Status=1 might mean 'confirmed stay' and it's NOT the same as r.Status
cursor.execute("""
    SELECT COUNT(dd.RecId) as Rooms, SUM(r.Pax + r.Childs) as Pax, SUM(r.Pax) as PaxOnly
    FROM DailyDetail dd
    LEFT JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
      AND dd.Status = 1
""")
row = cursor.fetchone()
print(f"dd.Status=1 All: Rooms={row[0]}, Pax+Childs={row[1]}, PaxOnly={row[2]}")

cursor.execute("""
    SELECT COUNT(dd.RecId) as Rooms, SUM(r.Pax + r.Childs) as Pax, SUM(r.Pax) as PaxOnly
    FROM DailyDetail dd
    LEFT JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
      AND dd.Status = 1
      AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
""")
row = cursor.fetchone()
print(f"dd.Status=1 No COMP: Rooms={row[0]}, Pax+Childs={row[1]}, PaxOnly={row[2]}")

print("\n=== ATTEMPT 5: CheckinDate-based query (reservations that START May 1-20) ===")
# Maybe 1462 includes FUTURE stays of reservations that checked in May 1-20
# i.e. total nights across all stay dates for those reservations
cursor.execute("""
    SELECT COUNT(dd.RecId) as RoomNights, SUM(r.Pax + r.Childs) as PaxNights
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE r.CheckinDate BETWEEN '20260501' AND '20260520'
      AND dd.Status != -1
      AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
""")
row = cursor.fetchone()
print(f"Res arriving May 1-20 (all stay days, no COMP): RoomNights={row[0]}, PaxNights={row[1]}")

cursor.execute("""
    SELECT COUNT(dd.RecId) as RoomNights, SUM(r.Pax + r.Childs) as PaxNights
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    WHERE r.CheckinDate BETWEEN '20260501' AND '20260520'
      AND dd.Status != -1
""")
row = cursor.fetchone()
print(f"Res arriving May 1-20 (all stay days, with COMP): RoomNights={row[0]}, PaxNights={row[1]}")

print("\n=== ATTEMPT 6: StayDate-based on DISTINCT RecId (rooms, not pax nights) ===")
cursor.execute("""
    SELECT SUM(cnt) FROM (
        SELECT dd.StayDate, COUNT(DISTINCT r.RecId) as cnt
        FROM DailyDetail dd
        JOIN Reservation r ON r.RecId = dd.ReservationId
        LEFT JOIN Agency a ON a.RecId = r.AgencyId
        WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
          AND dd.Status = 1
          AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
        GROUP BY dd.StayDate
    ) x
""")
row = cursor.fetchone()
print(f"Sum of DISTINCT RecId per day (dd.Status=1, no COMP): {row[0]}")

conn.close()
