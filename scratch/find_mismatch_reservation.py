import sys
sys.path.append("/home/society/Masaüstü/Sedna Dashboard")
import queries as Q
import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

# 1. SP rows for MUNFERIT TL
df_sp = Q._call_sp_revenue(conn, 2026, include_april=False)
sp_tl = df_sp[df_sp['AgencyCode'] == 'MUNFERIT TL']

# 2. DailyDetail stay dates for MUNFERIT TL
q = """
SELECT dd.StayDate, dd.ReservationId, r.Voucher, r.FirstName1 + ' ' + r.LastName1 AS Guest,
       dd.TotalRoomNetAmount, dd.Status AS dd_status, r.Status AS r_status
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
JOIN Agency a ON a.RecId = r.AgencyId
WHERE a.AgencyCode = 'MUNFERIT TL'
  AND YEAR(dd.StayDate) = 2026
  AND MONTH(dd.StayDate) BETWEEN 5 AND 10
  AND dd.Status != -1 AND r.Status != -1
ORDER BY dd.StayDate
"""
df_dd = pd.read_sql(q, conn)

print("--- DailyDetail Stay Dates for MUNFERIT TL ---")
print(df_dd.to_string())

# Since the SP has columns: PostDate (stay date), LocalAmount, and Board, let's group SP by PostDate and Board
sp_grouped = sp_tl.groupby(['PostDate', 'Board'])[['LocalAmount', 'RC_NetAmount']].sum().reset_index()
print("\n--- SP Output Stay Dates for MUNFERIT TL ---")
print(sp_grouped.to_string())

conn.close()
