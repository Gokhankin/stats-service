import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

q = """
SELECT r.RecId, r.Voucher, r.FirstName1, r.LastName1, r.RecordDate, r.UpdateDate, r.RecordUser, r.UpdateUser, r.CheckinDate, r.CheckoutDate, r.Status, r.Pax, a.AgencyCode,
       SUM(ISNULL(dd.ContrackPrice, 0)) as RevenueEUR,
       SUM(ISNULL(dd.TotalRoomNetAmount, 0)) as RevenueTRY,
       COUNT(dd.RecId) as RoomNights
FROM Reservation r
JOIN DailyDetail dd ON r.RecId = dd.ReservationId
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE (r.RecordDate >= CONVERT(datetime, '2026-05-25 09:30:00', 120) OR r.UpdateDate >= CONVERT(datetime, '2026-05-25 09:30:00', 120))
  AND YEAR(dd.StayDate) = 2026
  AND dd.Status != -1
  AND r.Status != -1
GROUP BY r.RecId, r.Voucher, r.FirstName1, r.LastName1, r.RecordDate, r.UpdateDate, r.RecordUser, r.UpdateUser, r.CheckinDate, r.CheckoutDate, r.Status, r.Pax, a.AgencyCode
ORDER BY r.UpdateDate DESC, r.RecordDate DESC
"""

df = pd.read_sql(q, conn)
df['RecordDateStr'] = df['RecordDate'].astype(str)
df['UpdateDateStr'] = df['UpdateDate'].astype(str)

print("--- Reservations created/updated after 09:30 AM today ---")
for idx, row in df.iterrows():
    print(f"ResId: {row['RecId']} | Voucher: {row['Voucher']} | Guest: {row['FirstName1']} {row['LastName1']} | RecDate: {row['RecordDateStr']} | UpdDate: {row['UpdateDateStr']} | User: {row['RecordUser']}/{row['UpdateUser']} | RoomNights: {row['RoomNights']} | EUR: {row['RevenueEUR']} | TRY: {row['RevenueTRY']}")

print("Total RoomNights of these changes:", df['RoomNights'].sum())
print("Total EUR Revenue of these changes:", df['RevenueEUR'].sum())
print("Total TRY Revenue of these changes:", df['RevenueTRY'].sum())

conn.close()
