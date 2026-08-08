import os, pyodbc, pandas as pd
from dotenv import load_dotenv
load_dotenv('/home/society/Masaüstü/stats/.env')
conn_str = os.getenv('DB_CONNECTION_STRING')
conn = pyodbc.connect(conn_str)

q = """
SELECT 
    r.RecId,
    ISNULL(r.Voucher, CAST(r.RecId AS VARCHAR)) as VoucherNo,
    ISNULL(r.FirstName1, '') + ' ' + ISNULL(r.LastName1, '') as GuestName,
    CONVERT(VARCHAR(10), r.CheckinDate, 120) as CheckinDate,
    CONVERT(VARCHAR(10), r.CheckOutDate, 120) as CheckoutDate,
    DATEDIFF(day, r.CheckinDate, r.CheckOutDate) as Nights,
    ISNULL(a.Name, ISNULL(a.AgencyCode, 'MÜNFERİT')) as AgencyName,
    r.Pax,
    r.Childs,
    1 as RoomCount,
    CONVERT(VARCHAR(16), r.RecordDate, 120) as RecordDate
FROM Reservation r
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE CAST(r.RecordDate AS DATE) = CAST(GETDATE() AS DATE)
  AND r.Status != -1
  AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
  AND ISNULL(r.LastName1, '') NOT IN ('aaa', 'TOLA', 'test', 'TEST', 'DUMMY')
  AND ISNULL(r.FirstName1, '') NOT IN ('aaa', 'TOLA', 'test', 'TEST', 'DUMMY')
ORDER BY r.CheckinDate ASC, r.RecordDate DESC
"""
df = pd.read_sql(q, conn)
print("TODAY ENTERED REZ COUNT:", len(df))
if not df.empty:
    print(df.to_string())
else:
    # Test recent records to see sample data if today has 0
    q_recent = """
    SELECT TOP 10
        r.RecId,
        ISNULL(r.Voucher, CAST(r.RecId AS VARCHAR)) as VoucherNo,
        ISNULL(r.FirstName1, '') + ' ' + ISNULL(r.LastName1, '') as GuestName,
        CONVERT(VARCHAR(10), r.CheckinDate, 120) as CheckinDate,
        CONVERT(VARCHAR(10), r.CheckOutDate, 120) as CheckoutDate,
        DATEDIFF(day, r.CheckinDate, r.CheckOutDate) as Nights,
        ISNULL(a.Name, ISNULL(a.AgencyCode, 'MÜNFERİT')) as AgencyName,
        r.Pax,
        r.Childs,
        CONVERT(VARCHAR(16), r.RecordDate, 120) as RecordDate
    FROM Reservation r
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE r.Status != -1
      AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
    ORDER BY r.RecordDate DESC
    """
    df_rec = pd.read_sql(q_recent, conn)
    print("MOST RECENT ENTERED REZ SAMPLE:")
    print(df_rec.to_string())

conn.close()
