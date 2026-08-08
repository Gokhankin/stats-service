import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

# Bugün 09:30'dan sonra güncellenen DailyDetail kayıtlarını bul (2026 sezonu)
q = """
SELECT
    r.RecId, r.Voucher, r.FirstName1, r.LastName1,
    a.AgencyCode,
    dd.StayDate, dd.ContrackPrice, dd.TotalRoomNetAmount,
    dd.Status AS dd_Status, r.Status AS r_Status,
    dd.UpdateDate AS dd_UpdateDate, dd.UpdateUser AS dd_UpdateUser,
    r.UpdateDate AS r_UpdateDate, r.UpdateUser AS r_UpdateUser
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
JOIN Agency a ON a.RecId = r.AgencyId
WHERE (dd.UpdateDate >= CONVERT(datetime, '2026-05-25 09:30:00', 120)
       OR dd.RecordDate >= CONVERT(datetime, '2026-05-25 09:30:00', 120))
  AND YEAR(dd.StayDate) = 2026
  AND dd.Status != -1
  AND r.Status != -1
ORDER BY dd.UpdateDate DESC, dd.RecordDate DESC
"""

df = pd.read_sql(q, conn)
print(f"Toplam güncellenen DailyDetail satırı: {len(df)}")
print()

# Acenta bazında grupla
by_agency = df.groupby('AgencyCode').agg(
    gece_sayisi=('StayDate', 'count'),
    toplam_eur=('ContrackPrice', 'sum'),
    ilk_guncelleme=('dd_UpdateDate', 'min'),
    son_guncelleme=('dd_UpdateDate', 'max')
).reset_index()
print("=== Acenta Bazında Özet ===")
print(by_agency.to_string())

print()
print("=== Rezervasyon Bazında Detay ===")
by_rez = df.groupby(['RecId','Voucher','FirstName1','LastName1','AgencyCode','r_UpdateDate']).agg(
    gece=('StayDate','count'),
    eur=('ContrackPrice','sum'),
    dd_guncelleme=('dd_UpdateDate','max')
).reset_index()
print(by_rez.to_string())

conn.close()
