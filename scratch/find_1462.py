import os
import sys
import pyodbc
from dotenv import load_dotenv

sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
CONN_STR = os.getenv("DB_CONNECTION_STRING")
conn = pyodbc.connect(CONN_STR)

cursor = conn.cursor()

# Let's try various queries to match 1462.
# 1. Could it be RoomNights?
# We saw Staying (1,2,3) with COMP = 1166 rooms, Pax = 2105.
# What about other reservation statuses? E.g., Status = 3 (Inhouse) only.
# Rooms = 919.
# What about RoomNights with Status = 3 (Inhouse) + Status = 1 (Expected arrival)?
# What about Status = 1 (Expected arrival) only? 
# Wait, let's print all combinations of r.Status and dd.Status.

print("--- TRYING COMBINATIONS ---")

# Let's check if 1462 is RoomNights or PaxNights
# We will query all dd.StayDate between '20260501' AND '20260520' and dd.Status != -1 (valid stays).
# Let's query:
# - Pax type (Pax only vs Pax + Childs)
# - Reservation Status filters: Status in (3), (2,3), (1,3), (1,2,3), (1,2,3,4)
# - Agency exclusions: None, COMP, NEILSON, etc.

r_statuses_options = [
    (1,), (2,), (3,), (4,),
    (1,2), (1,3), (2,3), (1,2,3), (1,2,3,4)
]

for r_status in r_statuses_options:
    status_str = ",".join(map(str, r_status))
    
    # Check 1: Pax + Childs, No COMP
    cursor.execute(f"""
        SELECT COUNT(dd.RecId) as Rooms, SUM(r.Pax + r.Childs) as Pax
        FROM DailyDetail dd
        JOIN Reservation r ON r.RecId = dd.ReservationId
        LEFT JOIN Agency a ON a.RecId = r.AgencyId
        WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
          AND dd.Status != -1
          AND r.Status IN ({status_str})
          AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
    """)
    res = cursor.fetchone()
    rooms, pax = res[0] or 0, res[1] or 0
    if abs(rooms - 1462) < 20:
        print(f"MATCH ROOMS (No COMP, r.Status={r_status}): Rooms = {rooms}, Pax = {pax}")
    if abs(pax - 1462) < 20:
        print(f"MATCH PAX (No COMP, r.Status={r_status}): Rooms = {rooms}, Pax = {pax}")

    # Check 2: Pax only (No Childs), No COMP
    cursor.execute(f"""
        SELECT COUNT(dd.RecId) as Rooms, SUM(r.Pax) as Pax
        FROM DailyDetail dd
        JOIN Reservation r ON r.RecId = dd.ReservationId
        LEFT JOIN Agency a ON a.RecId = r.AgencyId
        WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
          AND dd.Status != -1
          AND r.Status IN ({status_str})
          AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
    """)
    res = cursor.fetchone()
    rooms, pax = res[0] or 0, res[1] or 0
    if abs(pax - 1462) < 20:
        print(f"MATCH PAX ONLY (No COMP, r.Status={r_status}): Rooms = {rooms}, Pax = {pax}")

    # Check 3: Pax + Childs, WITH COMP
    cursor.execute(f"""
        SELECT COUNT(dd.RecId) as Rooms, SUM(r.Pax + r.Childs) as Pax
        FROM DailyDetail dd
        JOIN Reservation r ON r.RecId = dd.ReservationId
        WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
          AND dd.Status != -1
          AND r.Status IN ({status_str})
    """)
    res = cursor.fetchone()
    rooms, pax = res[0] or 0, res[1] or 0
    if abs(rooms - 1462) < 20:
        print(f"MATCH ROOMS (With COMP, r.Status={r_status}): Rooms = {rooms}, Pax = {pax}")
    if abs(pax - 1462) < 20:
        print(f"MATCH PAX (With COMP, r.Status={r_status}): Rooms = {rooms}, Pax = {pax}")

    # Check 4: Pax only (No Childs), WITH COMP
    cursor.execute(f"""
        SELECT COUNT(dd.RecId) as Rooms, SUM(r.Pax) as Pax
        FROM DailyDetail dd
        JOIN Reservation r ON r.RecId = dd.ReservationId
        WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
          AND dd.Status != -1
          AND r.Status IN ({status_str})
    """)
    res = cursor.fetchone()
    rooms, pax = res[0] or 0, res[1] or 0
    if abs(pax - 1462) < 20:
        print(f"MATCH PAX ONLY (With COMP, r.Status={r_status}): Rooms = {rooms}, Pax = {pax}")

conn.close()
