import sys
sys.path.append("/home/society/Masaüstü/Sedna Dashboard")
import queries as Q
import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

df_sp = Q._call_sp_revenue(conn, 2026, include_april=False)
sp_touristica = df_sp[df_sp['AgencyCode'] == 'TOURISTICA']

print("--- TOURISTICA SP Whole Season ---")
print(f"SP Rooms Sum: {sp_touristica['RoomNummer'].sum()}")
print(f"SP TL Sum: {sp_touristica['LocalAmount'].sum():,.2f}")
print(f"SP EUR Sum: {sp_touristica['RC_NetAmount'].sum():,.2f}")
print("\nFirst 10 rows in SP:")
print(sp_touristica.head(10).to_string())

conn.close()
