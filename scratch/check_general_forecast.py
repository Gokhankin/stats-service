import os, sys, pyodbc, warnings
from dotenv import load_dotenv

sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
cursor = conn.cursor()
warnings.filterwarnings("ignore")

# 1. Önce Forecast veya benzer isimli tabloları bul
print("=== Forecast/Statistic ilgili tablolar ===")
cursor.execute("""
    SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    AND (TABLE_NAME LIKE '%Forecast%' OR TABLE_NAME LIKE '%General%' OR TABLE_NAME LIKE '%Stat%')
    ORDER BY TABLE_NAME
""")
tables = [r[0] for r in cursor.fetchall()]
print(tables)

# 2. DailyDetail'de dd.Status değerlerini ve anlamlarını tekrar kontrol et
# dd.Status = 1 => "Forecast" (Sedna'da onaylı rezervasyonların gelecek konaklamaları)
# Bu bizim 1139 oda / 2048 pax rakamımız
print("\n=== dd.Status=1 (General Forecast) - Mayıs 1-20, COMP hariç ===")
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
total_rooms = 0
total_pax = 0
for row in rows:
    print(f"  {row[0].strftime('%d Mayıs')}: {row[1]} oda, {row[2]} pax")
    total_rooms += row[1]
    total_pax += (row[2] or 0)
print(f"\n  TOPLAM: {total_rooms} oda-gece, {total_pax} kişi-gece")

# 3. dd.Status kodlarını görsel olarak kontrol et (Sedna terminolojisi)
print("\n=== Sedna DailyDetail Status Kodları ===")
cursor.execute("""
    SELECT dd.Status, COUNT(*) as cnt
    FROM DailyDetail dd
    WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
    GROUP BY dd.Status
    ORDER BY dd.Status
""")
status_map = {0: "Tentative?", 1: "General Forecast (Onaylı)", 2: "Block?", 3: "InHouse?", 4: "CheckedOut?", -1: "İptal"}
for row in cursor.fetchall():
    print(f"  Status={row[0]} ({status_map.get(row[0], '?')}): {row[1]} satır")

conn.close()
