import os, sys, pyodbc, warnings
import pandas as pd
from dotenv import load_dotenv

sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
cursor = conn.cursor()
warnings.filterwarnings("ignore")

NEILSON_ID = 1120
NEILSON_GUARANTEE_PER_DAY = 35
day_val = 20   # May 1-20 = 20 days
total_neilson_guarantee = NEILSON_GUARANTEE_PER_DAY * day_val  # = 700

print(f"Neilson guarantee for 20 days = {total_neilson_guarantee}")

# Our current logic: for each day, rooms = max(actual_neilson, guarantee)
# But our query counts UNIQUE reservations, not daily rows. Let's check daily breakdown:
cursor.execute("""
    SELECT dd.StayDate, COUNT(DISTINCT r.RecId) as RoomCount, SUM(r.Pax + r.Childs) as PaxCount
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
      AND dd.Status = 1
      AND r.AgencyId = 1120
    GROUP BY dd.StayDate
    ORDER BY dd.StayDate
""")
rows = cursor.fetchall()
neilson_actual_total = 0
neilson_guaranteed_total = 0
for r in rows:
    actual = r[1]
    guaranteed = max(actual, NEILSON_GUARANTEE_PER_DAY)
    neilson_actual_total += actual
    neilson_guaranteed_total += guaranteed
    print(f"  {r[0].strftime('%d-%m')} => Actual={actual}, Guaranteed={guaranteed}")

print(f"\nNeilson: Actual RoomNights={neilson_actual_total}, Guarantee-adjusted={neilson_guaranteed_total}")

# Now get other agencies (non-Neilson, non-COMP)
cursor.execute("""
    SELECT SUM(cnt) FROM (
        SELECT dd.StayDate, COUNT(DISTINCT r.RecId) as cnt
        FROM DailyDetail dd
        JOIN Reservation r ON r.RecId = dd.ReservationId
        LEFT JOIN Agency a ON a.RecId = r.AgencyId
        WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
          AND dd.Status = 1
          AND r.AgencyId != 1120
          AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
        GROUP BY dd.StayDate
    ) x
""")
other_rooms = cursor.fetchone()[0]
print(f"\nOther agencies (excl COMP+NEILSON): {other_rooms} room-nights")
total_with_guarantee = (neilson_guaranteed_total or 0) + (other_rooms or 0)
total_without_guarantee = (neilson_actual_total or 0) + (other_rooms or 0)
print(f"\nTotal WITH guarantee: {total_with_guarantee}")
print(f"Total WITHOUT guarantee: {total_without_guarantee}")

# Now let's also check ManagerReport for MonthlyTotalRoom or similar field
print("\n--- ManagerReport fields with values between 800-2000 ---")
sql = "SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='20260520', @AvailableRoom=0"
df = pd.read_sql(sql, conn)
for col in df.columns:
    val = df[col].iloc[0]
    if isinstance(val, (int, float)) and 800 <= val <= 2000 and not str(col).endswith('EUR') and not str(col).endswith('USD'):
        print(f"  {col}: {val}")

conn.close()
