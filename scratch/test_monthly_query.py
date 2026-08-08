import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

EXCLUDED_NAMES = "('aaa', 'TOLA', 'test', 'TEST', 'DUMMY')"
HIDDEN_AGENCIES = ['COMP']
COMMON_FILTER = f"""
  AND r.Status != -1
  AND a.AgencyCode NOT IN ('COMP')
  AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
"""

print("--- Query 1: Room Nights & Pax Nights in May 2026 via DailyDetail ---")
# Let us run the exact query used by get_monthly (Query 2. Oda-Gece Sayıları)
q_gece = f"""
    SELECT 
        MONTH(dd.StayDate) as ay,
        SUM(CASE WHEN (r.FirstName1 LIKE '%GROUP%' OR r.LastName1 LIKE '%GROUP%') THEN 
            CASE WHEN ISNULL(TRY_CAST(r.RoomNummer AS INT), 0) > ISNULL(r.Pax, 1) THEN TRY_CAST(r.RoomNummer AS INT) ELSE ISNULL(r.Pax, 1) END 
        ELSE 1 END) as night_room,
        SUM(CASE WHEN (r.FirstName1 LIKE '%GROUP%' OR r.LastName1 LIKE '%GROUP%') THEN 
            CASE WHEN ISNULL(TRY_CAST(r.RoomNummer AS INT), 0) > ISNULL(r.Pax, 1) THEN TRY_CAST(r.RoomNummer AS INT) ELSE ISNULL(r.Pax, 1) END 
        ELSE ISNULL(dd.Pax, 0) END) as night_pax
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    JOIN Agency a ON a.RecId = r.AgencyId
    WHERE YEAR(dd.StayDate) = 2026
      AND dd.Status != -1 
      {COMMON_FILTER}
      AND MONTH(dd.StayDate) = 5
    GROUP BY MONTH(dd.StayDate)
"""
df_gece = pd.read_sql(q_gece, conn)
print(df_gece)


print("\n--- Query 2: Simple COUNT of dd.StayDate (No Group RoomNummer logic) ---")
q_simple = f"""
    SELECT 
        COUNT(dd.RecId) as simple_rooms,
        SUM(ISNULL(dd.Pax, 0)) as simple_pax
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    JOIN Agency a ON a.RecId = r.AgencyId
    WHERE YEAR(dd.StayDate) = 2026
      AND dd.Status != -1
      {COMMON_FILTER}
      AND MONTH(dd.StayDate) = 5
"""
df_simple = pd.read_sql(q_simple, conn)
print(df_simple)

conn.close()
