import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

q = """
SELECT r.RecId AS ReservationId, r.Voucher, r.FirstName1 + ' ' + r.LastName1 AS Guest,
       r.CheckinDate, r.CheckoutDate, r.RecordDate, r.UpdateDate, r.Status,
       (SELECT SUM(TotalRoomNetAmount) FROM DailyDetail WHERE ReservationId = r.RecId AND Status != -1) as dd_net_sum,
       (SELECT COUNT(*) FROM DailyDetail WHERE ReservationId = r.RecId AND Status != -1) as dd_nights
FROM Reservation r
JOIN Agency a ON a.RecId = r.AgencyId
WHERE a.AgencyCode = 'MUNFERIT TL'
  AND YEAR(r.CheckinDate) = 2026
  AND r.Status != -1
ORDER BY r.CheckinDate
"""
df = pd.read_sql(q, conn)
print(df.to_string())

conn.close()
