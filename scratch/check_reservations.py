import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

# Common filter for COMP, dummy names, and cancelled reservations
EXCLUDED_NAMES = "('aaa', 'TOLA', 'test', 'TEST', 'DUMMY')"
COMMON_FILTER = f"""
  AND r.Status != -1
  AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
  AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
"""

query = f"""
SELECT 
    r.RecId as ReservationId,
    r.Voucher,
    r.LastName1,
    r.FirstName1,
    r.RecordDate,
    r.RecordUser,
    r.CheckinDate,
    r.CheckoutDate,
    r.Pax,
    r.Childs,
    COUNT(dd.StayDate) as RoomNights,
    SUM(dd.Pax) as BedNights
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE dd.StayDate BETWEEN '20260501' AND '20260531'
  AND dd.Status = 1
  {COMMON_FILTER}
GROUP BY r.RecId, r.Voucher, r.LastName1, r.FirstName1, r.RecordDate, r.RecordUser, r.CheckinDate, r.CheckoutDate, r.Pax, r.Childs
ORDER BY r.RecordDate DESC
"""

df = pd.read_sql(query, conn)
print("Total RoomNights in May 2026:", df["RoomNights"].sum())
print("Total BedNights in May 2026:", df["BedNights"].sum())
print("Total Unique Reservations in May 2026:", len(df))

# Filter for reservations entered on 2026-05-25 (Today)
df['RecordDateStr'] = df['RecordDate'].astype(str)
today_df = df[df['RecordDateStr'].str.startswith('2026-05-25')]

print("\n--- Reservations in May 2026 entered/recorded on 2026-05-25 (Today) ---")
for idx, row in today_df.iterrows():
    print(f"Voucher: {row['Voucher']} | Guest: {row['FirstName1']} {row['LastName1']} | RecDate: {row['RecordDate']} | User: {row['RecordUser']} | Pax: {row['Pax']}+{row['Childs']} | RoomNights: {row['RoomNights']} | BedNights: {row['BedNights']}")

print("\n--- All Reservations Entered Today (2026-05-25) ---")
q_all_today = f"""
SELECT r.RecId, r.Voucher, r.FirstName1, r.LastName1, r.RecordDate, r.RecordUser, r.CheckinDate, r.CheckoutDate, r.Pax, r.Childs, a.AgencyCode
FROM Reservation r
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE CAST(r.RecordDate AS DATE) = '2026-05-25'
  {COMMON_FILTER}
"""
df_all_today = pd.read_sql(q_all_today, conn)
print(df_all_today)

conn.close()
