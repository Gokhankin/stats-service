import os
import pyodbc
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
CONN_STR = os.getenv("DB_CONNECTION_STRING")

def audit_record_dates():
    conn = pyodbc.connect(CONN_STR)
    years = [2024, 2025, 2026]
    
    for year in years:
        print(f"\n--- Auditing Year {year} ---")
        query = f"""
        SELECT 
            COUNT(*) as TotalReservations,
            SUM(CASE WHEN RecordDate IS NULL THEN 1 ELSE 0 END) as NullRecordDate,
            SUM(CASE WHEN RecordDate IS NOT NULL AND RecordDate = '1900-01-01' THEN 1 ELSE 0 END) as DefaultRecordDate
        FROM Reservation
        WHERE YEAR(CheckinDate) = {year}
          AND Status != -1
        """
        df = pd.read_sql(query, conn)
        print(df)
        
        # Check if RecordDate is generally earlier than CheckinDate (as expected)
        query_check = f"""
        SELECT TOP 10 RecordDate, CheckinDate 
        FROM Reservation 
        WHERE YEAR(CheckinDate) = {year} AND Status != -1 AND RecordDate IS NOT NULL
        ORDER BY CheckinDate DESC
        """
        df_check = pd.read_sql(query_check, conn)
        print("\nSample Dates (RecordDate vs CheckinDate):")
        print(df_check)

    conn.close()

if __name__ == "__main__":
    audit_record_dates()
