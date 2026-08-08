import os, sys, pyodbc, pandas as pd
from dotenv import load_dotenv
sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
import warnings
warnings.filterwarnings("ignore")

# 1. MTD verisi (1 Mayıs - 22 Mayıs 2026)
sql = "SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='20260522', @AvailableRoom=111"
df = pd.read_sql(sql, conn)
row = df.iloc[0]

print("=== MTD 01.05-22.05/2026 (Excel: sevki.jpeg) ===")
print(f"  %Room (hedef: 51,74):")
for col in df.columns:
    if 'ratio' in col.lower() and 'monthly' in col.lower() and 'room' in col.lower():
        print(f"    {col}: {float(row[col]):.2f}")

print(f"\n  %Bed (hedef: 38,69):")
for col in df.columns:
    if 'ratio' in col.lower() and 'monthly' in col.lower() and 'bed' in col.lower():
        print(f"    {col}: {float(row[col]):.2f}")

print(f"\n  Bed Night (hedef: 2.253):")
for col in df.columns:
    if 'monthly' in col.lower() and ('pax' in col.lower() or 'bed' in col.lower()) and 'avr' not in col.lower() and 'ratio' not in col.lower() and 'revenue' not in col.lower():
        val = float(row[col])
        if val > 0:
            print(f"    {col}: {val:.0f}")

print(f"\n  Revenue (hedef: 195.221):")
print(f"    MonthlyNetRoomRevenueEUR: {float(row.get('MonthlyNetRoomRevenueEUR', 0)):.2f}")
print(f"    MonthlyRoomRevenueForeign: {float(row.get('MonthlyRoomRevenueForeign', 0)):.2f}")

print(f"\n  Avp Pax (hedef: 86,65):")
for col in df.columns:
    if 'monthly' in col.lower() and 'pax' in col.lower() and 'avr' in col.lower() and 'eur' in col.lower():
        print(f"    {col}: {float(row[col]):.2f}")

# 2. Tam Ay verisi (1-31 Mayıs 2026) - Forecast
print("\n\n=== FULL MONTH 01.05-31.05/2026 (Excel: sevki.jpeg) ===")
sql31 = "SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='20260531', @AvailableRoom=111"
df31 = pd.read_sql(sql31, conn)
row31 = df31.iloc[0]

print(f"  %Room (hedef: 50,35):")
for col in df31.columns:
    if 'ratio' in col.lower() and 'monthly' in col.lower() and 'room' in col.lower():
        print(f"    {col}: {float(row31[col]):.2f}")

print(f"\n  Bed Night (hedef: 3.128):")
for col in df31.columns:
    if 'monthly' in col.lower() and ('pax' in col.lower()) and 'avr' not in col.lower() and 'ratio' not in col.lower() and 'revenue' not in col.lower():
        val = float(row31[col])
        if val > 0:
            print(f"    {col}: {val:.0f}")

print(f"\n  Revenue (hedef: 294.946):")
print(f"    MonthlyNetRoomRevenueEUR: {float(row31.get('MonthlyNetRoomRevenueEUR', 0)):.2f}")

print(f"\n  Avp Pax (hedef: 94,29):")
for col in df31.columns:
    if 'monthly' in col.lower() and 'pax' in col.lower() and 'avr' in col.lower() and 'eur' in col.lower():
        print(f"    {col}: {float(row31[col]):.2f}")

# 3. LY MTD (2025)
print("\n\n=== LY MTD 01.05-22.05/2025 ===")
sql_ly = "SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='20250522', @AvailableRoom=111"
df_ly = pd.read_sql(sql_ly, conn)
row_ly = df_ly.iloc[0]
print(f"  %Room (hedef: 54,55): MonthlySoldRoomRatio = {float(row_ly.get('MonthlySoldRoomRatio', 0)):.2f}")
print(f"  Bed Night (hedef: 2.378): MonthlySoldPax = {float(row_ly.get('MonthlySoldPax', 0)):.0f}")
print(f"  Revenue (hedef: 210.421): MonthlyNetRoomRevenueEUR = {float(row_ly.get('MonthlyNetRoomRevenueEUR', 0)):.2f}")
print(f"  Avp Pax (hedef: 88,49): MonthlySoldPaxAvrEUR = {float(row_ly.get('MonthlySoldPaxAvrEUR', 0)):.2f}")
