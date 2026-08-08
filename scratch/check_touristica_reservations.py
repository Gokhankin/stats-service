import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

q = """
SELECT r.RecId, r.Voucher, r.FirstName1, r.LastName1, r.RecordDate, r.UpdateDate, r.CheckinDate, r.CheckoutDate, r.Status, r.Pax,
       SUM(ISNULL(dd.ContrackPrice, 0)) as RevenueEUR,
       SUM(ISNULL(dd.TotalRoomNetAmount, 0)) as RevenueTRY,
       COUNT(dd.RecId) as RoomNights
FROM Reservation r
JOIN DailyDetail dd ON r.RecId = dd.ReservationId
JOIN Agency a ON a.RecId = r.AgencyId
WHERE YEAR(dd.StayDate) = 2026
  AND MONTH(dd.StayDate) = 5
  AND dd.Status != -1
  AND r.Status != -1
  AND a.AgencyCode = 'TOURISTICA'
GROUP BY r.RecId, r.Voucher, r.FirstName1, r.LastName1, r.RecordDate, r.UpdateDate, r.CheckinDate, r.CheckoutDate, r.Status, r.Pax
ORDER BY r.UpdateDate DESC, r.RecordDate DESC
"""

df = pd.read_sql(q, conn)
print(df.to_string())
conn.close()
