import sys
sys.path.append("/home/society/Masaüstü/Sedna Dashboard")
import queries as Q
import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

# 1. Fetch SP output for TOURISTICA (which matches today's Excel totals)
df_sp = Q._call_sp_revenue(conn, 2026, include_april=False)
sp_touristica = df_sp[df_sp['AgencyCode'] == 'TOURISTICA']

print("--- TOURISTICA from SP ---")
print(f"Total TL: {sp_touristica['LocalAmount'].sum():,.2f}")
print(f"Total EUR: {sp_touristica['RC_NetAmount'].sum():,.2f}")
print(f"Total rooms: {sp_touristica['RoomNummer'].sum()}")
print(f"Total pax: {sp_touristica['Adult'].sum()}")

# Let's see the details grouped by stay date
sp_grouped = sp_touristica.groupby('PostDate').agg(
    sp_rooms=('RoomNummer', 'sum'),
    sp_pax=('Adult', 'sum'),
    sp_tl=('LocalAmount', 'sum'),
    sp_eur=('RC_NetAmount', 'sum')
).reset_index()

# 2. Fetch DailyDetail stay dates for TOURISTICA
q = """
SELECT dd.StayDate,
       COUNT(DISTINCT dd.ReservationId) AS dd_rez,
       SUM(CASE WHEN (r.FirstName1 LIKE '%GROUP%' OR r.LastName1 LIKE '%GROUP%') THEN 
           CASE WHEN ISNULL(TRY_CAST(r.RoomNummer AS INT), 0) > ISNULL(r.Pax, 1) THEN TRY_CAST(r.RoomNummer AS INT) ELSE ISNULL(r.Pax, 1) END 
       ELSE 1 END) AS dd_rooms,
       SUM(CASE WHEN (r.FirstName1 LIKE '%GROUP%' OR r.LastName1 LIKE '%GROUP%') THEN 
           CASE WHEN ISNULL(TRY_CAST(r.RoomNummer AS INT), 0) > ISNULL(r.Pax, 1) THEN TRY_CAST(r.RoomNummer AS INT) ELSE ISNULL(r.Pax, 1) END 
       ELSE ISNULL(dd.Pax, 0) END) AS dd_pax,
       SUM(dd.TotalRoomNetAmount) AS dd_tl,
       SUM(CASE WHEN dd.ContrackPrice > 0 THEN dd.ContrackPrice ELSE dd.TotalRoomNetAmount / 35.0 END) AS dd_eur
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
JOIN Agency a ON a.RecId = r.AgencyId
WHERE a.AgencyCode = 'TOURISTICA'
  AND YEAR(dd.StayDate) = 2026
  AND MONTH(dd.StayDate) = 5
  AND dd.Status != -1 AND r.Status != -1
GROUP BY dd.StayDate
ORDER BY dd.StayDate
"""
df_dd = pd.read_sql(q, conn)

merged = pd.merge(df_dd, sp_grouped, left_on='StayDate', right_on='PostDate', how='outer').fillna(0)
merged['room_diff'] = merged['dd_rooms'] - merged['sp_rooms']
merged['eur_diff'] = merged['dd_eur'] - merged['sp_eur']

print("\n--- DailyDetail vs SP (Stay Date level for May 2026) ---")
print(merged[['StayDate', 'dd_rooms', 'sp_rooms', 'room_diff', 'dd_eur', 'sp_eur', 'eur_diff']].to_string())

conn.close()
