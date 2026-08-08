import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

q = """
SELECT MONTH(dd.StayDate) AS StayMonth,
       COUNT(DISTINCT dd.ReservationId) AS dd_rez,
       SUM(CASE WHEN (r.FirstName1 LIKE '%GROUP%' OR r.LastName1 LIKE '%GROUP%') THEN 
           CASE WHEN ISNULL(TRY_CAST(r.RoomNummer AS INT), 0) > ISNULL(r.Pax, 1) THEN TRY_CAST(r.RoomNummer AS INT) ELSE ISNULL(r.Pax, 1) END 
       ELSE 1 END) AS dd_rooms,
       SUM(dd.TotalRoomNetAmount) AS dd_tl,
       SUM(CASE WHEN dd.ContrackPrice > 0 THEN dd.ContrackPrice ELSE dd.TotalRoomNetAmount / 35.0 END) AS dd_eur
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
JOIN Agency a ON a.RecId = r.AgencyId
WHERE a.AgencyCode = 'TOURISTICA'
  AND YEAR(dd.StayDate) = 2026
  AND dd.Status != -1 AND r.Status != -1
GROUP BY MONTH(dd.StayDate)
ORDER BY StayMonth
"""
df = pd.read_sql(q, conn)
print(df)

conn.close()
