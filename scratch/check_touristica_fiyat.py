import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

# Let's inspect the TOURISTICA reservations with stay dates in May 2026
q = """
SELECT dd.ReservationId, r.Voucher, r.FirstName1 + ' ' + r.LastName1 AS Misafir,
       dd.StayDate, dd.ContrackPrice, dd.TotalRoomNetAmount,
       dd.Status AS dd_Status,
       dd.RecordDate AS dd_KayitTarihi,
       dd.UpdateDate AS dd_GuncellemeTarihi,
       dd.UpdateUser
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
JOIN Agency a ON a.RecId = r.AgencyId
WHERE a.AgencyCode = 'TOURISTICA'
  AND YEAR(dd.StayDate) = 2026
  AND MONTH(dd.StayDate) = 5
  AND dd.Status != -1
ORDER BY dd.UpdateDate DESC, dd.ReservationId, dd.StayDate
"""
df = pd.read_sql(q, conn)
df['dd_KayitTarihiStr'] = df['dd_KayitTarihi'].astype(str)
df['dd_GuncellemeTarihiStr'] = df['dd_GuncellemeTarihi'].astype(str)

print("--- Touristica DailyDetails in May 2026 ---")
print(df[['ReservationId', 'Voucher', 'Misafir', 'StayDate', 'ContrackPrice', 'TotalRoomNetAmount', 'dd_GuncellemeTarihiStr', 'UpdateUser']].to_string())

conn.close()
