import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

# Find all reservations with stay dates in 2026 that were recorded or updated today (2026-05-25)
q = """
SELECT r.RecId, r.Voucher, r.FirstName1, r.LastName1, r.RecordDate, r.UpdateDate, r.RecordUser, r.UpdateUser, r.CheckinDate, r.CheckoutDate, r.Status, r.Pax, a.AgencyCode,
       SUM(ISNULL(dd.ContrackPrice, 0)) as RevenueEUR,
       SUM(ISNULL(dd.TotalRoomNetAmount, 0)) as RevenueTRY,
       COUNT(dd.RecId) as RoomNights
FROM Reservation r
JOIN DailyDetail dd ON r.RecId = dd.ReservationId
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE (CAST(r.RecordDate AS DATE) = '2026-05-25' OR CAST(r.UpdateDate AS DATE) = '2026-05-25')
  AND YEAR(dd.StayDate) = 2026
  AND dd.Status != -1
  AND r.Status != -1
GROUP BY r.RecId, r.Voucher, r.FirstName1, r.LastName1, r.RecordDate, r.UpdateDate, r.RecordUser, r.UpdateUser, r.CheckinDate, r.CheckoutDate, r.Status, r.Pax, a.AgencyCode
ORDER BY r.UpdateDate DESC, r.RecordDate DESC
"""

df = pd.read_sql(q, conn)
print(df)
conn.close()
