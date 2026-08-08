import os
import sys
import pyodbc
from dotenv import load_dotenv

sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
CONN_STR = os.getenv("DB_CONNECTION_STRING")
conn = pyodbc.connect(CONN_STR)

cursor = conn.cursor()

r_statuses_options = [
    (1,), (2,), (3,), (4,),
    (1,2), (1,3), (2,3), (1,2,3), (1,2,3,4)
]

for year in [2024, 2025, 2026]:
    print(f"\n=== CHECKING YEAR {year} ===")
    for r_status in r_statuses_options:
        status_str = ",".join(map(str, r_status))
        
        # Check 1: Pax + Childs, No COMP
        cursor.execute(f"""
            SELECT COUNT(dd.RecId) as Rooms, SUM(r.Pax + r.Childs) as Pax
            FROM DailyDetail dd
            JOIN Reservation r ON r.RecId = dd.ReservationId
            LEFT JOIN Agency a ON a.RecId = r.AgencyId
            WHERE dd.StayDate BETWEEN '{year}0501' AND '{year}0520'
              AND dd.Status != -1
              AND r.Status IN ({status_str})
              AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
        """)
        res = cursor.fetchone()
        rooms, pax = res[0] or 0, res[1] or 0
        if abs(rooms - 1462) < 25 or abs(pax - 1462) < 25:
            print(f"MATCH (No COMP, r.Status={r_status}): Rooms={rooms}, Pax={pax}")

        # Check 2: Pax only, No COMP
        cursor.execute(f"""
            SELECT COUNT(dd.RecId) as Rooms, SUM(r.Pax) as Pax
            FROM DailyDetail dd
            JOIN Reservation r ON r.RecId = dd.ReservationId
            LEFT JOIN Agency a ON a.RecId = r.AgencyId
            WHERE dd.StayDate BETWEEN '{year}0501' AND '{year}0520'
              AND dd.Status != -1
              AND r.Status IN ({status_str})
              AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
        """)
        res = cursor.fetchone()
        rooms, pax = res[0] or 0, res[1] or 0
        if abs(pax - 1462) < 25:
            print(f"MATCH PAX ONLY (No COMP, r.Status={r_status}): Rooms={rooms}, Pax={pax}")

        # Check 3: Pax + Childs, WITH COMP
        cursor.execute(f"""
            SELECT COUNT(dd.RecId) as Rooms, SUM(r.Pax + r.Childs) as Pax
            FROM DailyDetail dd
            JOIN Reservation r ON r.RecId = dd.ReservationId
            WHERE dd.StayDate BETWEEN '{year}0501' AND '{year}0520'
              AND dd.Status != -1
              AND r.Status IN ({status_str})
        """)
        res = cursor.fetchone()
        rooms, pax = res[0] or 0, res[1] or 0
        if abs(rooms - 1462) < 25 or abs(pax - 1462) < 25:
            print(f"MATCH (With COMP, r.Status={r_status}): Rooms={rooms}, Pax={pax}")

        # Check 4: Pax only, WITH COMP
        cursor.execute(f"""
            SELECT COUNT(dd.RecId) as Rooms, SUM(r.Pax) as Pax
            FROM DailyDetail dd
            JOIN Reservation r ON r.RecId = dd.ReservationId
            WHERE dd.StayDate BETWEEN '{year}0501' AND '{year}0520'
              AND dd.Status != -1
              AND r.Status IN ({status_str})
        """)
        res = cursor.fetchone()
        rooms, pax = res[0] or 0, res[1] or 0
        if abs(pax - 1462) < 25:
            print(f"MATCH PAX ONLY (With COMP, r.Status={r_status}): Rooms={rooms}, Pax={pax}")

conn.close()
