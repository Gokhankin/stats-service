import os
import sys
import pyodbc
from dotenv import load_dotenv

sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
CONN_STR = os.getenv("DB_CONNECTION_STRING")
conn = pyodbc.connect(CONN_STR)

cursor = conn.cursor()

# Exhaustive check of sums/counts in DailyDetail and Reservation for May 1-20, 2026.
# Let's check different combinations of status, agency, room types, etc.

# 1. Total Pax Nights (Pax + Childs) in DailyDetail where dd.StayDate BETWEEN '20260501' AND '20260520'
# Let's check:
# - Including/excluding COMP, Neilson, etc.
# - Group by dd.Status
# - Group by r.Status
# - Filter combinations

print("--- SEARCHING 1462 IN DAILYDETAIL STAYS (1-20 May 2026) ---")

# Let's test all subsets of dd.Status (0, 1, 2, 3, 4)
# Let's write a recursive function or loop to find if any subset of dd.Status sums to 1462
from itertools import combinations

dd_statuses = [0, 1, 2, 3, 4]
for r in range(1, len(dd_statuses) + 1):
    for subset in combinations(dd_statuses, r):
        # We will query RoomNights and PaxNights for this subset of dd.Status
        subset_str = ",".join(map(str, subset))
        
        # Scenario A: All agencies (including COMP)
        cursor.execute(f"""
            SELECT COUNT(dd.RecId) as Rooms, SUM(r.Pax + r.Childs) as Pax
            FROM DailyDetail dd
            LEFT JOIN Reservation r ON r.RecId = dd.ReservationId
            WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
              AND dd.Status IN ({subset_str})
        """)
        rooms, pax = cursor.fetchone()
        rooms = rooms or 0
        pax = pax or 0
        if abs(rooms - 1462) < 10:
            print(f"dd.Status subset {subset} (with COMP) -> Rooms = {rooms} (MATCH!)")
        if abs(pax - 1462) < 10:
            print(f"dd.Status subset {subset} (with COMP) -> Pax = {pax} (MATCH!)")
            
        # Scenario B: Excluding COMP
        cursor.execute(f"""
            SELECT COUNT(dd.RecId) as Rooms, SUM(r.Pax + r.Childs) as Pax
            FROM DailyDetail dd
            LEFT JOIN Reservation r ON r.RecId = dd.ReservationId
            LEFT JOIN Agency a ON a.RecId = r.AgencyId
            WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
              AND dd.Status IN ({subset_str})
              AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
        """)
        rooms, pax = cursor.fetchone()
        rooms = rooms or 0
        pax = pax or 0
        if abs(rooms - 1462) < 10:
            print(f"dd.Status subset {subset} (excl COMP) -> Rooms = {rooms} (MATCH!)")
        if abs(pax - 1462) < 10:
            print(f"dd.Status subset {subset} (excl COMP) -> Pax = {pax} (MATCH!)")

print("\n--- SEARCHING 1462 IN RESERVATIONS BOOKED OR ARRIVING ---")
# Could 1462 be the sum of Pax for reservations whose CHECKIN date is between 1-20 May 2026?
# Or checkin date in May 2026?
cursor.execute("""
    SELECT COUNT(r.RecId) as Rooms, SUM(r.Pax + r.Childs) as Pax
    FROM Reservation r
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE r.CheckinDate BETWEEN '20260501' AND '20260520'
      AND r.Status != -1
""")
rooms, pax = cursor.fetchone()
print(f"Arriving 1-20 May (with COMP): Rooms = {rooms}, Pax = {pax}")

cursor.execute("""
    SELECT COUNT(r.RecId) as Rooms, SUM(r.Pax + r.Childs) as Pax
    FROM Reservation r
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE r.CheckinDate BETWEEN '20260501' AND '20260520'
      AND r.Status != -1
      AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
""")
rooms, pax = cursor.fetchone()
print(f"Arriving 1-20 May (excl COMP): Rooms = {rooms}, Pax = {pax}")

# Let's check checkin date in the entire month of May 2026
cursor.execute("""
    SELECT COUNT(r.RecId) as Rooms, SUM(r.Pax + r.Childs) as Pax
    FROM Reservation r
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE r.CheckinDate BETWEEN '20260501' AND '20260531'
      AND r.Status != -1
""")
rooms, pax = cursor.fetchone()
print(f"Arriving entire May (with COMP): Rooms = {rooms}, Pax = {pax}")

# Let's check Neilson guarantee calculations
# Could 1462 be Neilson's guarantee + others?
# What is the total sum of stay days in 1-20 May?
# Let's check other combinations.

conn.close()
