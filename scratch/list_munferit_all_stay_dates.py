import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

q = """
SELECT dd.ReservationId, r.Voucher, r.FirstName1 + ' ' + r.LastName1 AS Guest,
       dd.StayDate, dd.TotalRoomNetAmount, dd.ContrackPrice, dd.Status AS dd_status, r.Status AS r_status
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
JOIN Agency a ON a.RecId = r.AgencyId
WHERE a.AgencyCode = 'MUNFERIT TL'
  AND dd.StayDate BETWEEN '2026-05-01' AND '2026-10-31'
  AND dd.Status != -1 AND r.Status != -1
ORDER BY dd.StayDate, dd.ReservationId
"""
df = pd.read_sql(q, conn)
print(df.to_string())

conn.close()
