import os, sys, pyodbc, pandas as pd
from dotenv import load_dotenv
sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
import warnings
warnings.filterwarnings("ignore")

# Query SP daily revenue for each day in May
total = 0
for day in range(1, 23):
    date_str = f"202605{day:02d}"
    sql = f"SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='{date_str}', @AvailableRoom=0"
    df = pd.read_sql(sql, conn)
    row = df.iloc[0]
    daily_rev = float(row.get('DailyNetRoomRevenueEUR', row.get('DailyRoomRevenueEUR', 0.0)))
    total += daily_rev
    print(f"{date_str}: {daily_rev:,.2f} | Cumulative: {total:,.2f}")
