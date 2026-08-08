import os
import pyodbc
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
CONN_STR = os.getenv("DB_CONNECTION_STRING")

def final_audit():
    conn = pyodbc.connect(CONN_STR)
    
    print("--- 2026 MAY 1-15 AUDIT ---")
    query = """
    SELECT 
        COUNT(*) as TotalRoomNights,
        SUM(Pax) as TotalAdults,
        SUM(Childs) as TotalChildren,
        SUM(Pax + Childs) as TotalPax
    FROM DailyDetail
    WHERE StayDate BETWEEN '20260501' AND '20260515'
      AND Status = 1
    """
    df = pd.read_sql(query, conn)
    print(df)
    
    print("\n--- STATUS BREAKDOWN ---")
    query_status = """
    SELECT Status, COUNT(*) as Count
    FROM DailyDetail
    WHERE StayDate BETWEEN '20260501' AND '20260515'
    GROUP BY Status
    """
    df_status = pd.read_sql(query_status, conn)
    print(df_status)

    conn.close()

if __name__ == "__main__":
    final_audit()
