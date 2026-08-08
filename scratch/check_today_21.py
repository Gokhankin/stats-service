import os
import pyodbc
from dotenv import load_dotenv

load_dotenv("/home/society/Masaüstü/stats/.env")
CONN_STR = os.getenv("DB_CONNECTION_STRING")
conn = pyodbc.connect(CONN_STR)

EXCLUDED_NAMES = ('aaa', 'TOLA', 'test', 'TEST', 'DUMMY')

# Today's date: 2026-05-21
target_date = "20260521"
yesterday_date = "20260520"

# 1. Total staying guests today (without COMP)
query_today_pax = f"""
SELECT ISNULL(SUM(r.Pax + r.Childs), 0) as DailyPax, COUNT(DISTINCT r.RecId) as Rooms
FROM DailyDetail dd
JOIN Reservation r ON r.RecId = dd.ReservationId
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE dd.StayDate = '{target_date}'
  AND dd.Status != -1
  AND r.Status IN (1, 2, 3)
  AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
"""

# 2. Check-ins today (reservations with CheckinDate = today)
query_checkins = f"""
SELECT r.FirstName1, r.LastName1, r.Pax, r.Childs, a.AgencyCode, r.Status
FROM Reservation r
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE CAST(r.CheckinDate AS DATE) = '2026-05-21'
  AND r.Status IN (1, 2, 3)
  AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
"""

# 3. Check-outs today (reservations with CheckoutDate = today)
query_checkouts = f"""
SELECT r.FirstName1, r.LastName1, r.Pax, r.Childs, a.AgencyCode, r.Status
FROM Reservation r
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE CAST(r.CheckoutDate AS DATE) = '2026-05-21'
  AND r.Status IN (1, 2, 3, 4)
  AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
"""

# 4. Entered today (RecordDate = today)
query_entered_today = f"""
SELECT r.FirstName1, r.LastName1, r.Pax, r.Childs, a.AgencyCode, r.CheckinDate, r.CheckoutDate
FROM Reservation r
LEFT JOIN Agency a ON a.RecId = r.AgencyId
WHERE CAST(r.RecordDate AS DATE) = '2026-05-21'
  AND r.Status != -1
  AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
  AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
"""

cursor = conn.cursor()

# Execute 1
cursor.execute(query_today_pax)
pax, rooms = cursor.fetchone()

# Execute 2
cursor.execute(query_checkins)
checkins = cursor.fetchall()

# Execute 3
cursor.execute(query_checkouts)
checkouts = cursor.fetchall()

# Execute 4
cursor.execute(query_entered_today)
entered = cursor.fetchall()

print(f"TODAY_PAX: {pax}")
print(f"TODAY_ROOMS: {rooms}")
print("\n--- CHECK-INS (GİRİŞ YAPANLAR) ---")
for r in checkins:
    print(f"Name: {r[0]} {r[1]} | Pax: {r[2]} | Agency: {r[4]} | Status: {r[5]}")

print("\n--- CHECK-OUTS (ÇIKIŞ YAPANLAR) ---")
for r in checkouts:
    print(f"Name: {r[0]} {r[1]} | Pax: {r[2]} | Agency: {r[4]} | Status: {r[5]}")

print("\n--- ENTERED TODAY (BUGÜN GİRİLEN REZERVASYONLAR) ---")
for r in entered:
    print(f"Name: {r[0]} {r[1]} | Pax: {r[2]} | Agency: {r[4]} | Stay: {r[5].strftime('%Y-%m-%d')} to {r[6].strftime('%Y-%m-%d')}")

conn.close()
