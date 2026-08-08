import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

q = """
SELECT StayDate, ContrackPrice, TotalRoomNetAmount, RecordDate, RecordUser, UpdateDate, UpdateUser
FROM DailyDetail
WHERE ReservationId = 29662
ORDER BY StayDate
"""
df = pd.read_sql(q, conn)
print(df)
conn.close()
