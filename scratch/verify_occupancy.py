import os, sys, pyodbc, pandas as pd
from dotenv import load_dotenv
sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
import warnings
warnings.filterwarnings("ignore")

AVAILABLE_ROOMS = 111
AVAILABLE_BEDS = 222

# MTD: 1 Mayıs - 22 Mayıs 2026
cursor = conn.cursor()
cursor.execute("""
    SELECT 
        COUNT(dd.ReservationId) as SoldRoomNights,
        ISNULL(SUM(dd.Pax), 0) as BedNights
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate BETWEEN '20260501' AND '20260522'
      AND dd.Status = 1
      AND r.Status != -1
      AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
      AND ISNULL(r.LastName1, '') NOT IN ('aaa','TOLA','test','TEST','DUMMY')
      AND ISNULL(r.FirstName1, '') NOT IN ('aaa','TOLA','test','TEST','DUMMY')
""")
row = cursor.fetchone()
sold_rooms = int(row[0])
bed_nights = int(row[1])
days = 22
avail_room_nights = AVAILABLE_ROOMS * days
avail_bed_nights = AVAILABLE_BEDS * days

pct_room = (sold_rooms / avail_room_nights) * 100
pct_bed = (bed_nights / avail_bed_nights) * 100

print(f"=== Manual Calculation MTD 01.05-22.05/2026 ===")
print(f"  Sold Room Nights: {sold_rooms}")
print(f"  Available Room Nights: {avail_room_nights}")
print(f"  %Room: {pct_room:.2f} (hedef: 51,74)")
print(f"  Bed Nights: {bed_nights}")
print(f"  Available Bed Nights: {avail_bed_nights}")
print(f"  %Bed: {pct_bed:.2f} (hedef: 38,69)")

# LY: 1 Mayıs - 22 Mayıs 2025
cursor.execute("""
    SELECT 
        COUNT(dd.ReservationId) as SoldRoomNights,
        ISNULL(SUM(dd.Pax), 0) as BedNights
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate BETWEEN '20250501' AND '20250522'
      AND dd.Status = 1
      AND r.Status != -1
      AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
      AND ISNULL(r.LastName1, '') NOT IN ('aaa','TOLA','test','TEST','DUMMY')
      AND ISNULL(r.FirstName1, '') NOT IN ('aaa','TOLA','test','TEST','DUMMY')
""")
row_ly = cursor.fetchone()
ly_sold_rooms = int(row_ly[0])
ly_bed_nights = int(row_ly[1])

ly_pct_room = (ly_sold_rooms / avail_room_nights) * 100
ly_pct_bed = (ly_bed_nights / avail_bed_nights) * 100

print(f"\n=== LY MTD 01.05-22.05/2025 ===")
print(f"  Sold Room Nights: {ly_sold_rooms}")
print(f"  %Room: {ly_pct_room:.2f} (hedef: 54,55)")
print(f"  Bed Nights: {ly_bed_nights}")
print(f"  %Bed: {ly_pct_bed:.2f} (hedef: 40,48)")

# Full Month Forecast: 1-31 Mayıs 2026
cursor.execute("""
    SELECT 
        COUNT(dd.ReservationId) as SoldRoomNights,
        ISNULL(SUM(dd.Pax), 0) as BedNights
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate BETWEEN '20260501' AND '20260531'
      AND dd.Status = 1
      AND r.Status != -1
      AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
      AND ISNULL(r.LastName1, '') NOT IN ('aaa','TOLA','test','TEST','DUMMY')
      AND ISNULL(r.FirstName1, '') NOT IN ('aaa','TOLA','test','TEST','DUMMY')
""")
row_fm = cursor.fetchone()
fm_sold_rooms = int(row_fm[0])
fm_bed_nights = int(row_fm[1])
fm_days = 31
fm_avail_room_nights = AVAILABLE_ROOMS * fm_days
fm_avail_bed_nights = AVAILABLE_BEDS * fm_days

fm_pct_room = (fm_sold_rooms / fm_avail_room_nights) * 100
fm_pct_bed = (fm_bed_nights / fm_avail_bed_nights) * 100

print(f"\n=== Full Month 01.05-31.05/2026 ===")
print(f"  Sold Room Nights: {fm_sold_rooms}")
print(f"  %Room: {fm_pct_room:.2f} (hedef: 50,35)")
print(f"  Bed Nights: {fm_bed_nights}")
print(f"  %Bed: {fm_pct_bed:.2f} (hedef: 38,11)")
