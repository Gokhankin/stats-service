import sys
sys.path.append("/home/society/Masaüstü/Sedna Dashboard")
import queries as Q
import pyodbc

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

df = Q.get_agency_folio_revenue(conn, 2026, include_april=False)
print("--- get_agency_folio_revenue with include_april=False ---")
print(df[df['acenta'].isin(['MUNFERIT TL', 'MUNFERIT EURO', 'MUNFERIT GBP', 'MUNFERIT EURO'])][['acenta', 'night_room', 'night_pax', 'gelir_tl', 'gelir_raw']])

print("\n--- Total for all agencies ---")
print(f"Total TL: {df['gelir_tl'].sum():,.2f}")
print(f"Total EUR: {df['gelir_raw'].sum():,.2f}")
print(f"Total rooms: {df['night_room'].sum()}")
print(f"Total pax: {df['night_pax'].sum()}")

conn.close()
