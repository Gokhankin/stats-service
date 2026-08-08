import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

q = """
SELECT TOP 5 dd.ReservationId, r.Voucher, r.FirstName1 + ' ' + r.LastName1 AS Guest,
       dd.StayDate, dd.ContrackPrice, dd.TotalRoomNetAmount,
       dd.Status
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
JOIN Agency a ON a.RecId = r.AgencyId
WHERE a.AgencyCode = 'TOURISTICA'
  AND YEAR(dd.StayDate) = 2026
  AND MONTH(dd.StayDate) = 5
  AND dd.Status != -1
ORDER BY dd.StayDate
"""
df = pd.read_sql(q, conn)
print(df.to_string())

conn.close()
