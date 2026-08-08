import pyodbc
import pandas as pd
import sys
sys.path.append("/home/society/Masaüstü/Sedna Dashboard")
import queries as Q

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

print("--- Calling get_agency_folio_revenue (2026, include_april=False) ---")
df_folio = Q.get_agency_folio_revenue(conn, 2026, include_april=False)
print("Columns:", df_folio.columns.tolist())
print(df_folio[['acenta', 'night_room', 'night_pax', 'gelir_raw', 'gelir_tl']])
print("Total RoomNights:", df_folio['night_room'].sum())
print("Total BedNights:", df_folio['night_pax'].sum())
print("Total Revenue EUR:", df_folio['gelir_raw'].sum())
print("Total Revenue TRY:", df_folio['gelir_tl'].sum())

conn.close()
