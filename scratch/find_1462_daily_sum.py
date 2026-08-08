import os, sys, pyodbc, warnings
from dotenv import load_dotenv

sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
cursor = conn.cursor()
warnings.filterwarnings("ignore")

print("=== Günlük konaklayan kişi sayısı toplamı (1-20 Mayıs) ===")
print("(Asıl hipotez: 1462 = her günkü misafir sayısının toplamı)")
print()

# dd.Status=1 (confirmed stay), no COMP
cursor.execute("""
    SELECT dd.StayDate, 
           COUNT(DISTINCT dd.ReservationId) as Rooms,
           SUM(r.Pax + r.Childs) as Pax
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
      AND dd.Status = 1
      AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
      AND ISNULL(r.LastName1, '') NOT IN ('aaa','TOLA','test','TEST','DUMMY')
    GROUP BY dd.StayDate
    ORDER BY dd.StayDate
""")
rows = cursor.fetchall()
total_pax = 0
total_rooms = 0
for row in rows:
    print(f"  {row[0].strftime('%d Mayıs')}: {row[1]} oda, {row[2]} kişi")
    total_rooms += row[1]
    total_pax += (row[2] or 0)
print(f"\n  TOPLAM (dd.Status=1, no COMP): {total_rooms} oda-gece, {total_pax} kişi-gece")

print()

# dd.Status=1, WITH COMP
cursor.execute("""
    SELECT SUM(daily_pax) FROM (
        SELECT dd.StayDate, SUM(r.Pax + r.Childs) as daily_pax
        FROM DailyDetail dd
        JOIN Reservation r ON r.RecId = dd.ReservationId
        WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
          AND dd.Status = 1
        GROUP BY dd.StayDate
    ) t
""")
row = cursor.fetchone()
print(f"  TOPLAM (dd.Status=1, WITH COMP): {row[0]} kişi-gece")

# r.Status=3 (InHouse), no COMP
cursor.execute("""
    SELECT SUM(daily_pax) FROM (
        SELECT dd.StayDate, SUM(r.Pax + r.Childs) as daily_pax
        FROM DailyDetail dd
        JOIN Reservation r ON r.RecId = dd.ReservationId
        LEFT JOIN Agency a ON a.RecId = r.AgencyId
        WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
          AND dd.Status = 1
          AND r.Status = 3
          AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
        GROUP BY dd.StayDate
    ) t
""")
row = cursor.fetchone()
print(f"  TOPLAM (dd.Status=1, r.Status=3 InHouse, no COMP): {row[0]} kişi-gece")

# r.Status = 3, WITH COMP (gerçek InHouse)
cursor.execute("""
    SELECT SUM(daily_pax) FROM (
        SELECT dd.StayDate, SUM(r.Pax + r.Childs) as daily_pax
        FROM DailyDetail dd
        JOIN Reservation r ON r.RecId = dd.ReservationId
        WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
          AND dd.Status = 1
          AND r.Status = 3
        GROUP BY dd.StayDate
    ) t
""")
row = cursor.fetchone()
print(f"  TOPLAM (dd.Status=1, r.Status=3 InHouse, WITH COMP): {row[0]} kişi-gece")

# r.Status IN (2, 3), no COMP
cursor.execute("""
    SELECT SUM(daily_pax) FROM (
        SELECT dd.StayDate, SUM(r.Pax + r.Childs) as daily_pax
        FROM DailyDetail dd
        JOIN Reservation r ON r.RecId = dd.ReservationId
        LEFT JOIN Agency a ON a.RecId = r.AgencyId
        WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
          AND dd.Status = 1
          AND r.Status IN (2,3)
          AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
        GROUP BY dd.StayDate
    ) t
""")
row = cursor.fetchone()
print(f"  TOPLAM (dd.Status=1, r.Status IN (2,3), no COMP): {row[0]} kişi-gece")

# r.Status IN (1,2,3), no COMP, no NEILSON UNUSED
cursor.execute("""
    SELECT SUM(daily_pax) FROM (
        SELECT dd.StayDate, SUM(r.Pax + r.Childs) as daily_pax
        FROM DailyDetail dd
        JOIN Reservation r ON r.RecId = dd.ReservationId
        LEFT JOIN Agency a ON a.RecId = r.AgencyId
        WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
          AND dd.Status = 1
          AND r.Status IN (1,2,3)
          AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
          AND r.LastName1 NOT LIKE '%UNUSED%'
        GROUP BY dd.StayDate
    ) t
""")
row = cursor.fetchone()
print(f"  TOPLAM (dd.Status=1, r.Status=1,2,3, no COMP, no UNUSED): {row[0]} kişi-gece")

conn.close()
