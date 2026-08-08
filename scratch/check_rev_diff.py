import os, sys, pyodbc, pandas as pd
from dotenv import load_dotenv
sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
import warnings
warnings.filterwarnings("ignore")

cursor = conn.cursor()

# Get folio sum for May 1-22
cursor.execute("""
    SELECT IsNull(Sum(Case When F.CurrencyCode = 'EUR' Then F.NetAmount Else F.NetAmount*(Dbo.FnFoundCurr(IsNull(F.CurrDate,F.Postdate),F.CurrencyCode,1,1)/Dbo.FnFoundCurr(IsNull(F.CurrDate,F.PostDate),'EUR',1,1)) End),0)
    FROM Department D, Folio F
    WHERE F.CompanyRecId=1 and D.CompanyRecId=1 and D.DepartCode = F.DepartCode AND D.DepartType = 1 And F.Deleted = 0
      AND F.PostDate BETWEEN '20260501' AND '20260522'
""")
folio_sum = cursor.fetchone()[0]

# Get forecast sum for May 1-31 from DailyDetail ?
# How is Forecast Revenue calculated in Sedna?
cursor.execute("""
    SELECT SUM(ISNULL(dd.Price, 0))
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    WHERE dd.StayDate BETWEEN '20260501' AND '20260531'
      AND dd.Status = 1
""")
dd_sum = cursor.fetchone()[0]

print("Folio Sum 1-22 May:", folio_sum)
print("DailyDetail Price Sum 1-31 May:", dd_sum)

# What about ManagerReport 2026-05-31?
sql31 = "SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='20260531', @AvailableRoom=111"
df31 = pd.read_sql(sql31, conn)
row31 = df31.iloc[0]
print("SP 31 May MonthlyNetRoomRevenueEUR:", float(row31.get('MonthlyNetRoomRevenueEUR', 0)))

