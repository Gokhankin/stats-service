import os
import pyodbc
from dotenv import load_dotenv

load_dotenv("/home/society/Masaüstü/stats/.env")
CONN_STR = os.getenv("DB_CONNECTION_STRING")
conn = pyodbc.connect(CONN_STR)

EXCLUDED_NAMES = ('aaa', 'TOLA', 'test', 'TEST', 'DUMMY')
as_of_month_day = "05-20"

for year in [2025, 2026]:
    # 1. Daily Pax - With COMP
    daily_with_comp_query = f"""
    SELECT ISNULL(SUM(r.Pax + r.Childs), 0) as DailyPax
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    WHERE dd.StayDate = '{year}{as_of_month_day.replace("-", "")}'
      AND dd.Status != -1
      AND r.Status IN (1, 2, 3)
      AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
      AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
    """

    # 2. Daily Pax - Without COMP
    daily_without_comp_query = f"""
    SELECT ISNULL(SUM(r.Pax + r.Childs), 0) as DailyPax
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate = '{year}{as_of_month_day.replace("-", "")}'
      AND dd.Status != -1
      AND r.Status IN (1, 2, 3)
      AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
      AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
      AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
    """

    # 3. Night/Monthly Pax - With COMP
    monthly_with_comp_query = f"""
    SELECT ISNULL(SUM(r.Pax + r.Childs), 0) as PaxCount
    FROM Reservation r
    WHERE CAST(ISNULL(r.RecordDate, r.CheckinDate) AS DATE) BETWEEN '{year}0501' AND '{year}{as_of_month_day.replace("-", "")}'
      AND YEAR(r.CheckinDate) = {year}
      AND r.Status IN (1, 2, 3, 4)
      AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
      AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
    """

    # 4. Night/Monthly Pax - Without COMP
    monthly_without_comp_query = f"""
    SELECT ISNULL(SUM(r.Pax + r.Childs), 0) as PaxCount
    FROM Reservation r
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE CAST(ISNULL(r.RecordDate, r.CheckinDate) AS DATE) BETWEEN '{year}0501' AND '{year}{as_of_month_day.replace("-", "")}'
      AND YEAR(r.CheckinDate) = {year}
      AND r.Status IN (1, 2, 3, 4)
      AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
      AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
      AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
    """

    cursor = conn.cursor()
    
    cursor.execute(daily_with_comp_query)
    d_with = cursor.fetchone()[0]
    
    cursor.execute(daily_without_comp_query)
    d_without = cursor.fetchone()[0]
    
    cursor.execute(monthly_with_comp_query)
    m_with = cursor.fetchone()[0]
    
    cursor.execute(monthly_without_comp_query)
    m_without = cursor.fetchone()[0]
    
    print(f"YEAR {year}:")
    print(f"  Daily PAX (With COMP):    {d_with}")
    print(f"  Daily PAX (Without COMP): {d_without}  (Diff: -{d_with - d_without})")
    print(f"  Monthly PAX (With COMP):    {m_with}")
    print(f"  Monthly PAX (Without COMP): {m_without}  (Diff: -{m_with - m_without})")
    print()

conn.close()
