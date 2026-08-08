import sys
sys.path.append("/home/society/Masaüstü/Sedna Dashboard")
import queries as Q
import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

df = Q.get_agency_folio_revenue(conn, 2026)
print("--- Current 2026 Agency Folio Revenue Output ---")
print(df.to_string())
print("\nTotals from query:")
print(f"Total Rez (Reservations): {df['rez'].sum()}")
print(f"Total Rooms (Gece): {df['night_room'].sum()}")
print(f"Total Pax (night_pax): {df['night_pax'].sum()}")
print(f"Total TL (gelir_tl): {df['gelir_tl'].sum():,.2f}")
print(f"Total EUR (gelir_raw): {df['gelir_raw'].sum():,.2f}")

conn.close()
