import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

q = """
SELECT TOP 5 *
FROM DailyDetail
WHERE ReservationId = 29665
"""
df = pd.read_sql(q, conn)
print("--- Columns and values for reservation 29665 ---")
for col in df.columns:
    print(f"{col}: {df[col].iloc[0]}")

conn.close()
