import sys
sys.path.append("/home/society/Masaüstü/Sedna Dashboard")
import queries as Q
import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

# 1. Fetch from SP
df_sp = Q._call_sp_revenue(conn, 2026, include_april=False)
sp_tl = df_sp[df_sp['AgencyCode'] == 'MUNFERIT TL']
print("=== MUNFERIT TL rows in SP ===")
print(sp_tl.to_string())
print(f"SP MUNFERIT TL Sum: LocalAmount={sp_tl['LocalAmount'].sum():,.2f}, RC_NetAmount={sp_tl['RC_NetAmount'].sum():,.2f}")

# 2. Fetch from DailyDetail
q = """
SELECT dd.ReservationId, r.Voucher, r.FirstName1 + ' ' + r.LastName1 AS Guest,
       SUM(dd.TotalRoomNetAmount) AS dd_tl_sum,
       SUM(dd.ContrackPrice) AS dd_eur_sum,
       COUNT(dd.RecId) AS dd_rooms
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
JOIN Agency a ON a.RecId = r.AgencyId
WHERE a.AgencyCode = 'MUNFERIT TL'
  AND YEAR(dd.StayDate) = 2026
  AND MONTH(dd.StayDate) BETWEEN 5 AND 10
  AND dd.Status != -1 AND r.Status != -1
GROUP BY dd.ReservationId, r.Voucher, r.FirstName1, r.LastName1
ORDER BY dd.ReservationId
"""
df_dd = pd.read_sql(q, conn)
print("\n=== MUNFERIT TL reservations in DailyDetail (StayDates May-Oct) ===")
print(df_dd.to_string())
print(f"DailyDetail MUNFERIT TL Sum: dd_tl_sum={df_dd['dd_tl_sum'].sum():,.2f}, dd_rooms={df_dd['dd_rooms'].sum()}")

conn.close()
