import sys
sys.path.append("/home/society/Masaüstü/Sedna Dashboard")
import queries as Q
import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

df_sp = Q._call_sp_revenue(conn, 2026, include_april=False)
sp_touristica = df_sp[df_sp['AgencyCode'] == 'TOURISTICA']

q = """
SELECT dd.StayDate,
       SUM(CASE WHEN (r.FirstName1 LIKE '%GROUP%' OR r.LastName1 LIKE '%GROUP%') THEN 
           CASE WHEN ISNULL(TRY_CAST(r.RoomNummer AS INT), 0) > ISNULL(r.Pax, 1) THEN TRY_CAST(r.RoomNummer AS INT) ELSE ISNULL(r.Pax, 1) END 
       ELSE 1 END) AS dd_rooms,
       SUM(dd.TotalRoomNetAmount) AS dd_tl
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
JOIN Agency a ON a.RecId = r.AgencyId
WHERE a.AgencyCode = 'TOURISTICA'
  AND YEAR(dd.StayDate) = 2026
  AND MONTH(dd.StayDate) = 5
  AND dd.Status != -1 AND r.Status != -1
GROUP BY dd.StayDate
"""
df_dd = pd.read_sql(q, conn)

print("df_dd StayDate type:", df_dd['StayDate'].dtype)
print("df_sp PostDate type:", sp_touristica['PostDate'].dtype)

# Convert both to string YYYY-MM-DD
df_dd['date_str'] = pd.to_datetime(df_dd['StayDate']).dt.strftime('%Y-%m-%d')
sp_touristica['date_str'] = pd.to_datetime(sp_touristica['PostDate']).dt.strftime('%Y-%m-%d')

sp_grouped = sp_touristica.groupby('date_str').agg(
    sp_rooms=('RoomNummer', 'sum'),
    sp_tl=('LocalAmount', 'sum'),
    sp_eur=('RC_NetAmount', 'sum')
).reset_index()

merged = pd.merge(df_dd, sp_grouped, on='date_str', how='outer').fillna(0)
merged['room_diff'] = merged['dd_rooms'] - merged['sp_rooms']
merged['tl_diff'] = merged['dd_tl'] - merged['sp_tl']

print("\n--- Corrected Comparison (May 2026) ---")
print(merged[['date_str', 'dd_rooms', 'sp_rooms', 'room_diff', 'dd_tl', 'sp_tl', 'tl_diff']].to_string())

conn.close()
