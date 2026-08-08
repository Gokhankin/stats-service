import os
import pyodbc
import pandas as pd
from dotenv import load_dotenv
import queries as Q

load_dotenv()
CONN_STR = os.getenv("DB_CONNECTION_STRING")

def test_full_stats():
    conn = pyodbc.connect(CONN_STR)
    as_of_date = "05-15"
    
    for year in [2024, 2025, 2026]:
        print(f"\n--- Testing Year {year} ---")
        try:
            # We need to see the queries
            season_start = f"{year}0501"
            season_end = f"{year}1031"
            cap_query = f"SELECT COUNT(DISTINCT Room) as RoomCount FROM DailyDetail WHERE StayDate BETWEEN '{season_start}' AND '{season_end}' AND Status != -1"
            df_cap = pd.read_sql(cap_query, conn)
            year_capacity = int(df_cap.iloc[0]['RoomCount'] or 111)
            print(f"Year Capacity: {year_capacity}")
            
            stats = Q.get_year_stats(conn, year, as_of_date)
            print(f"Occupancy: {stats['Occupancy']:.2f}%")
            print(f"NightRoom (MTD): {stats['NightRoom']}")
        except Exception as e:
            print(f"Error for {year}: {e}")
    
    conn.close()

if __name__ == "__main__":
    test_full_stats()
