import sys
sys.path.append("/home/society/Masaüstü/Sedna Dashboard")
import queries as Q
import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

df_sp = Q._call_sp_revenue(conn, 2026, include_april=True)
print("Columns in SP output:", df_sp.columns)

walkins = df_sp[df_sp['AgencyCode'].isin(['MUNFERIT TL', 'MUNFERIT EURO', 'MUNFERIT GBP'])]
print("\n--- Walk-in rows in SP output ---")
print(walkins[['AgencyCode', 'AgencyName', 'LocalAmount', 'RC_NetAmount', 'RoomNummer', 'Adult']].to_string())

conn.close()
