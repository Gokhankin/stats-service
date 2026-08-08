import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

EXCLUDED_NAMES = "('aaa', 'TOLA', 'test', 'TEST', 'DUMMY')"
COMMON_FILTER = f"""
  AND r.Status != -1
  AND a.AgencyCode NOT IN ('COMP')
  AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
"""

# Let's get every reservation with stays in May 2026
query = f"""
SELECT 
    r.RecId as ResId,
    r.Voucher,
    r.FirstName1,
    r.LastName1,
    r.RecordDate,
    r.UpdateDate,
    r.RecordUser,
    r.UpdateUser,
    r.CheckinDate,
    r.CheckoutDate,
    r.Status,
    r.Pax,
    r.Childs,
    a.AgencyCode,
    COUNT(dd.StayDate) as RoomNights,
    SUM(dd.Pax) as BedNights,
    SUM(ISNULL(dd.ContrackPrice, 0)) as RevenueEUR,
    SUM(ISNULL(dd.TotalRoomNetAmount, 0)) as RevenueTRY
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE dd.StayDate BETWEEN '20260501' AND '20260531'
  AND dd.Status = 1
  {COMMON_FILTER}
GROUP BY r.RecId, r.Voucher, r.FirstName1, r.LastName1, r.RecordDate, r.UpdateDate, r.RecordUser, r.UpdateUser, r.CheckinDate, r.CheckoutDate, r.Status, r.Pax, r.Childs, a.AgencyCode
ORDER BY r.RecordDate DESC
"""

df = pd.read_sql(query, conn)
df.to_csv("/home/society/Masaüstü/stats/scratch/may_reservations_detail.csv", index=False)

# Let's see if any have RecordDate or UpdateDate starting with 2026-05-25 (Today)
df['RecordDateStr'] = df['RecordDate'].astype(str)
df['UpdateDateStr'] = df['UpdateDate'].astype(str)

today_created = df[df['RecordDateStr'].str.startswith('2026-05-25')]
today_updated = df[df['UpdateDateStr'].str.startswith('2026-05-25')]

print(f"Total reservations in May 2026: {len(df)}")
print(f"Total RoomNights in May 2026: {df['RoomNights'].sum()}")
print(f"Total BedNights in May 2026: {df['BedNights'].sum()}")
print(f"Total Revenue EUR in May 2026: {df['RevenueEUR'].sum()}")
print(f"Total Revenue TRY in May 2026: {df['RevenueTRY'].sum()}")

print("\n--- Created Today (2026-05-25) in May 2026 stays ---")
print(today_created[['ResId', 'Voucher', 'FirstName1', 'LastName1', 'RecordDate', 'AgencyCode', 'RoomNights', 'Pax']])

print("\n--- Updated Today (2026-05-25) in May 2026 stays ---")
print(today_updated[['ResId', 'Voucher', 'FirstName1', 'LastName1', 'UpdateDate', 'UpdateUser', 'AgencyCode', 'RoomNights', 'Pax']])

# Let's also check recently created (yesterday 2026-05-24)
yesterday_created = df[df['RecordDateStr'].str.startswith('2026-05-24')]
print("\n--- Created Yesterday (2026-05-24) in May 2026 stays ---")
print(yesterday_created[['ResId', 'Voucher', 'FirstName1', 'LastName1', 'RecordDate', 'AgencyCode', 'RoomNights', 'Pax']])

conn.close()
