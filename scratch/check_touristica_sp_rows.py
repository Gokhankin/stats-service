import pyodbc
import sys
sys.path.append("/home/society/Masaüstü/Sedna Dashboard")
import queries as Q
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

df_sp = Q._call_sp_revenue(conn, 2026, include_april=False)
touristica_sp = df_sp[df_sp['AgencyCode'] == 'TOURISTICA']

# Let's write out all rows
print("--- TOURISTICA raw SP rows ---")
# columns typically returned by SP: Voucher, FirstName, LastName, StayDate, RoomNummer, Adult, RC_NetAmount, LocalAmount etc.
# let's print all available columns
print("Available columns:", touristica_sp.columns.tolist())
pd.set_option('display.max_rows', 200)
print(touristica_sp.to_string())

conn.close()
