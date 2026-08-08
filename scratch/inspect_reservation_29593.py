import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

q_res = "SELECT * FROM Reservation WHERE RecId = 29593"
df_res = pd.read_sql(q_res, conn)
print("--- Reservation 29593 ---")
for col in df_res.columns:
    val = df_res.loc[0, col]
    if pd.notna(val) and val != "":
        print(f"{col}: {val}")

q_dd = "SELECT * FROM DailyDetail WHERE ReservationId = 29593"
df_dd = pd.read_sql(q_dd, conn)
print("\n--- DailyDetail for 29593 ---")
print(df_dd[['StayDate', 'ContrackPrice', 'TotalRoomNetAmount', 'RoomNummer', 'Pax', 'Childs', 'Status']].to_string())

conn.close()
