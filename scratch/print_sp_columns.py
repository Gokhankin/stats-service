import sys
sys.path.append("/home/society/Masaüstü/Sedna Dashboard")
import queries as Q
import pyodbc

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

df_sp = Q._call_sp_revenue(conn, 2026, include_april=False)
print("SP output columns:")
print(df_sp.columns.tolist())
print("\nFirst row of SP output:")
print(df_sp.iloc[0].to_dict())

conn.close()
