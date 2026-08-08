import os
import pyodbc
from dotenv import load_dotenv
import queries as Q

load_dotenv("/home/society/Masaüstü/stats/.env")
CONN_STR = os.getenv("DB_CONNECTION_STRING")
conn = pyodbc.connect(CONN_STR)

YEARS = [2024, 2025, 2026]
as_of_date = "06-01"

print("--- RUNNING LIVE STATS QUERIES ---")
data = Q.get_all_stats(conn, YEARS, as_of_date)
conn.close()

for year, stats in data.items():
    print(f"\n--- YEAR: {year} ---")
    for k, v in stats.items():
        print(f"{k}: {v}")
