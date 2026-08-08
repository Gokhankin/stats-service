import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

q = """
SELECT r.RecId AS ReservationId, r.Voucher, r.FirstName1 + ' ' + r.LastName1 AS Guest,
       r.CheckinDate, r.CheckoutDate, r.Status, r.RecordDate, r.UpdateDate,
       (SELECT COUNT(*) FROM DailyDetail WHERE ReservationId = r.RecId AND Status != -1) as dd_nights,
       (SELECT SUM(TotalRoomNetAmount) FROM DailyDetail WHERE ReservationId = r.RecId AND Status != -1) as dd_net_sum,
       (SELECT SUM(ContrackPrice) FROM DailyDetail WHERE ReservationId = r.RecId AND Status != -1) as dd_contrack_sum
FROM Reservation r
JOIN Agency a ON a.RecId = r.AgencyId
WHERE a.AgencyCode = 'TOURISTICA'
  AND YEAR(r.CheckinDate) = 2026
  AND r.Status != -1
ORDER BY r.CheckinDate
"""
df = pd.read_sql(q, conn)
print(df.to_string())

conn.close()
