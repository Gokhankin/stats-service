import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

# Search in DailyDetail for MUNFERIT TL
print("\n--- Searching DailyDetail stay dates for MUNFERIT TL in 2026 ---")
q2 = """
SELECT dd.ReservationId, r.Voucher, r.FirstName1 + ' ' + r.LastName1 AS Guest,
       dd.StayDate, dd.TotalRoomNetAmount AS dd_net, dd.Status AS dd_status, r.Status AS r_status
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
JOIN Agency a ON a.RecId = r.AgencyId
WHERE a.AgencyCode = 'MUNFERIT TL'
  AND YEAR(dd.StayDate) = 2026
  AND dd.Status != -1 AND r.Status != -1
ORDER BY dd.StayDate
"""
df2 = pd.read_sql(q2, conn)
# Print all distinct reservations in DailyDetail with their total room net amount
print(df2.groupby(['ReservationId', 'Voucher', 'Guest', 'r_status']).agg(
    total_dd_net=('dd_net', 'first'),
    stay_dates_count=('dd_net', 'count')
).reset_index())


conn.close()
