import os, sys, pyodbc, pandas as pd
from dotenv import load_dotenv
sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
import warnings
warnings.filterwarnings("ignore")

# Let's print the daily RoomRevenueEUR from Folio for May 1 to May 22
cursor = conn.cursor()
cursor.execute("""
    SELECT F.PostDate, IsNull(Sum(Case When F.CurrencyCode = 'EUR' Then F.NetAmount Else F.NetAmount*(Dbo.FnFoundCurr(IsNull(F.CurrDate,F.Postdate),F.CurrencyCode,1,1)/Dbo.FnFoundCurr(IsNull(F.CurrDate,F.PostDate),'EUR',1,1)) End),0) As DailyRoomRevenueEUR
    FROM Department D, Folio F
    WHERE F.CompanyRecId=1 and D.CompanyRecId=1 and D.DepartCode = F.DepartCode AND D.DepartType = 1 And F.Deleted = 0
      AND F.PostDate BETWEEN '20260501' AND '20260522'
    GROUP BY F.PostDate
    ORDER BY F.PostDate
""")
rows = cursor.fetchall()
total = 0
for r in rows:
    total += float(r[1])
    print(f"{r[0].strftime('%Y-%m-%d')}: {float(r[1]):,.2f} | Cumulative: {total:,.2f}")
