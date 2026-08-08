import pyodbc
import sys
sys.path.append("/home/society/Masaüstü/Sedna Dashboard")
import queries as Q

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

# Get live folio revenue (which calls the SP)
df_folio = Q.get_agency_folio_revenue(conn, 2026, include_april=False)
touristica_folio = df_folio[df_folio['acenta'] == 'TOURISTICA']
print("--- TOURISTICA in get_agency_folio_revenue (SP) ---")
print(touristica_folio[['acenta', 'night_room', 'night_pax', 'gelir_raw', 'gelir_tl']])

# Call SP directly
df_sp = Q._call_sp_revenue(conn, 2026, include_april=False)
touristica_sp = df_sp[df_sp['AgencyCode'] == 'TOURISTICA']
print("\n--- TOURISTICA in raw SP result ---")
print(touristica_sp[['AgencyCode', 'RoomNummer', 'Adult', 'RC_NetAmount', 'LocalAmount']])

# Call Direct SQL
df_dir = Q._get_agency_direct_sql(conn, 2026, include_april=False)
touristica_dir = df_dir[df_dir['acenta'] == 'TOURISTICA']
print("\n--- TOURISTICA in direct SQL result ---")
print(touristica_dir[['acenta', 'night_room', 'night_pax', 'gelir_raw', 'gelir_tl']])

conn.close()
