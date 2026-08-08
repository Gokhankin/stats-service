import sys
sys.path.append("/home/society/Masaüstü/Sedna Dashboard")
import queries as Q
import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

# 1. SP rows
df_sp = Q._call_sp_revenue(conn, 2026, include_april=False)
sp_tl = df_sp[df_sp['AgencyCode'] == 'MUNFERIT TL']

# 2. DailyDetail rows (stay dates May-Oct)
q = """
SELECT dd.ReservationId, r.Voucher, r.FirstName1 + ' ' + r.LastName1 AS Guest,
       dd.StayDate, dd.TotalRoomNetAmount, dd.ContrackPrice, dd.Status AS dd_status, r.Status AS r_status
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
JOIN Agency a ON a.RecId = r.AgencyId
WHERE a.AgencyCode = 'MUNFERIT TL'
  AND YEAR(dd.StayDate) = 2026
  AND MONTH(dd.StayDate) BETWEEN 5 AND 10
  AND dd.Status != -1 AND r.Status != -1
ORDER BY dd.ReservationId, dd.StayDate
"""
df_dd = pd.read_sql(q, conn)

print("--- Comparing SP and DailyDetail ---")
# Let's find for each reservation in DailyDetail, what is its status, checkin, checkout, and total net amount.
# We also want to check if it's in the SP.
# Since the SP is aggregated by PostDate, let's group SP by PostDate and compare sums.
sp_by_date = sp_tl.groupby('PostDate')['LocalAmount'].sum().reset_index().rename(columns={'PostDate': 'StayDate', 'LocalAmount': 'sp_amount'})
dd_by_date = df_dd.groupby('StayDate')['TotalRoomNetAmount'].sum().reset_index().rename(columns={'TotalRoomNetAmount': 'dd_amount'})


merged = pd.merge(dd_by_date, sp_by_date, on='StayDate', how='outer').fillna(0)
merged['diff'] = merged['dd_amount'] - merged['sp_amount']
print("\n--- Stay Date Comparison ---")
print(merged[merged['diff'] != 0].to_string())

conn.close()
