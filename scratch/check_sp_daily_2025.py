import os, sys, pyodbc, pandas as pd
from dotenv import load_dotenv
sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
import warnings
warnings.filterwarnings("ignore")

# Query SP daily revenue for each day in May last year (2025)
total = 0
for day in range(1, 23):
    date_str = f"202505{day:02d}"
    sql = f"SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='{date_str}', @AvailableRoom=0"
    df = pd.read_sql(sql, conn)
    row = df.iloc[0]
    daily_rev = float(row.get('DailyNetRoomRevenueEUR', row.get('DailyRoomRevenueEUR', 0.0)))
    total += daily_rev
    print(f"{date_str}: {daily_rev:,.2f} | Cumulative: {total:,.2f}")

# Also get the MonthlyNetRoomRevenueEUR from SP on 2025-05-22
sql_mt = "SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='20250522', @AvailableRoom=0"
df_mt = pd.read_sql(sql_mt, conn)
row_mt = df_mt.iloc[0]
print("SP MonthlyNetRoomRevenueEUR on 2025-05-22:", float(row_mt.get('MonthlyNetRoomRevenueEUR', 0.0)))
