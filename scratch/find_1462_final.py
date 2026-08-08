import os, sys, pyodbc, warnings
from dotenv import load_dotenv

sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
cursor = conn.cursor()
warnings.filterwarnings("ignore")

print("=== SENARYO A: Rezervasyon tablosunda Mayıs 1-20 arası giriş yapan rezervasyonların TOPLAM GECELEME (Nights) toplamı ===")
# Bu Sedna'nın standart aylık raporunda kullandığı yaklaşım olabilir
cursor.execute("""
    SELECT 
        r.Status,
        COUNT(r.RecId) as RezCount,
        SUM(r.Nights) as TotalNights,
        SUM(r.Pax + r.Childs) as TotalPax,
        SUM(r.Nights * (r.Pax + r.Childs)) as PaxNights
    FROM Reservation r
    WHERE r.CheckinDate BETWEEN '20260501' AND '20260520'
    GROUP BY r.Status
    ORDER BY r.Status
""")
rows = cursor.fetchall()
for row in rows:
    print(f"  Status={row[0]}: Rezler={row[1]}, ToplamGece={row[2]}, ToplamPax={row[3]}, PaxGece={row[4]}")

print("\n=== SENARYO B: Mayıs 1-20 arasında KONAKLAYAN rezervasyonların PAX × geceleme toplamı ===")
# Rezervasyonun konakladığı günler Mayıs 1-20 içinde kesişen kısmı için
cursor.execute("""
    SELECT
        r.Status,
        COUNT(DISTINCT r.RecId) as RezCount,
        SUM(
            DATEDIFF(day, 
                CASE WHEN r.CheckinDate < '20260501' THEN '20260501' ELSE r.CheckinDate END,
                CASE WHEN r.CheckoutDate > '20260521' THEN '20260521' ELSE r.CheckoutDate END
            ) * (r.Pax + r.Childs)
        ) as OverlapPaxNights,
        SUM(
            DATEDIFF(day, 
                CASE WHEN r.CheckinDate < '20260501' THEN '20260501' ELSE r.CheckinDate END,
                CASE WHEN r.CheckoutDate > '20260521' THEN '20260521' ELSE r.CheckoutDate END
            )
        ) as OverlapRoomNights
    FROM Reservation r
    WHERE r.CheckinDate < '20260521' AND r.CheckoutDate > '20260501'
      AND r.Status NOT IN (-1, 0)
    GROUP BY r.Status
    ORDER BY r.Status
""")
rows = cursor.fetchall()
grand_pax_nights = 0
grand_room_nights = 0
for row in rows:
    print(f"  Status={row[0]}: Rez={row[1]}, ÜstüşenPaxGece={row[2]}, ÜstüşenOdaGece={row[3]}")
    grand_pax_nights += (row[2] or 0)
    grand_room_nights += (row[3] or 0)
print(f"  TOPLAM: PaxGece={grand_pax_nights}, OdaGece={grand_room_nights}")

print("\n=== SENARYO C: Sadece Status=1 (kesinleşmiş), COMP hariç, kesişim hesabı ===")
cursor.execute("""
    SELECT
        COUNT(DISTINCT r.RecId) as RezCount,
        SUM(
            DATEDIFF(day, 
                CASE WHEN r.CheckinDate < '20260501' THEN '20260501' ELSE r.CheckinDate END,
                CASE WHEN r.CheckoutDate > '20260521' THEN '20260521' ELSE r.CheckoutDate END
            ) * (r.Pax + r.Childs)
        ) as OverlapPaxNights,
        SUM(
            DATEDIFF(day, 
                CASE WHEN r.CheckinDate < '20260501' THEN '20260501' ELSE r.CheckinDate END,
                CASE WHEN r.CheckoutDate > '20260521' THEN '20260521' ELSE r.CheckoutDate END
            )
        ) as OverlapRoomNights
    FROM Reservation r
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE r.CheckinDate < '20260521' AND r.CheckoutDate > '20260501'
      AND r.Status = 1
      AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
""")
row = cursor.fetchone()
print(f"  Status=1, No COMP: Rez={row[0]}, PaxGece={row[1]}, OdaGece={row[2]}")

print("\n=== SENARYO D: Günlük inhouse sayısı — Sedna ManagerReport'un MonthlyTotalPax nasıl hesaplanıyor? ===")
# ManagerReport'taki MonthlyTotalPax = 2132 neydi?
# Let's check with Status IN (3) — actual inhouse counts per day summed
cursor.execute("""
    SELECT SUM(daily_pax) FROM (
        SELECT dd.StayDate, SUM(r.Pax + r.Childs) as daily_pax
        FROM DailyDetail dd
        JOIN Reservation r ON r.RecId = dd.ReservationId
        WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
          AND dd.Status IN (1, 3)
        GROUP BY dd.StayDate
    ) t
""")
row = cursor.fetchone()
print(f"  dd.Status IN (1,3) per day sum: {row[0]}")

cursor.execute("""
    SELECT SUM(daily_pax) FROM (
        SELECT dd.StayDate, SUM(r.Pax + r.Childs) as daily_pax
        FROM DailyDetail dd
        JOIN Reservation r ON r.RecId = dd.ReservationId
        LEFT JOIN Agency a ON a.RecId = r.AgencyId
        WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
          AND dd.Status IN (1)
          AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
        GROUP BY dd.StayDate
    ) t
""")
row = cursor.fetchone()
print(f"  dd.Status=1, No COMP per day sum: {row[0]}")

# What about checking the 'VoucherNight' or something in reservation?
print("\n=== SENARYO E: r.Nights alanı kullanılarak, Mayıs 1-20 arası CheckinDate filtresi ===")
for status_tuple in [(1,), (1,2), (1,3), (1,2,3), (2,3), (3,)]:
    status_str = ",".join(map(str, status_tuple))
    cursor.execute(f"""
        SELECT COUNT(r.RecId), SUM(r.Nights), SUM(r.Pax+r.Childs), SUM(r.Nights*(r.Pax+r.Childs))
        FROM Reservation r
        LEFT JOIN Agency a ON a.RecId = r.AgencyId
        WHERE r.CheckinDate BETWEEN '20260501' AND '20260520'
          AND r.Status IN ({status_str})
          AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
    """)
    row = cursor.fetchone()
    print(f"  CheckinDate May1-20, r.Status IN {status_tuple}, No COMP: Rez={row[0]}, Nights={row[1]}, Pax={row[2]}, PaxNights={row[3]}")
    
    cursor.execute(f"""
        SELECT COUNT(r.RecId), SUM(r.Nights), SUM(r.Pax+r.Childs), SUM(r.Nights*(r.Pax+r.Childs))
        FROM Reservation r
        WHERE r.CheckinDate BETWEEN '20260501' AND '20260520'
          AND r.Status IN ({status_str})
    """)
    row = cursor.fetchone()
    print(f"  CheckinDate May1-20, r.Status IN {status_tuple}, WITH COMP: Rez={row[0]}, Nights={row[1]}, Pax={row[2]}, PaxNights={row[3]}")

conn.close()
