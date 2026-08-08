import os, sys, pyodbc, pandas as pd
from dotenv import load_dotenv
sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
import warnings
warnings.filterwarnings("ignore")

cursor = conn.cursor()
cursor.execute("""
    SELECT IsNull(Sum(Case When F.CurrencyCode = 'EUR' Then F.NetAmount Else F.NetAmount*(Dbo.FnFoundCurr(IsNull(F.CurrDate,F.Postdate),F.CurrencyCode,1,1)/Dbo.FnFoundCurr(IsNull(F.CurrDate,F.PostDate),'EUR',1,1)) End),0) As TotalNetEUR
    FROM Department D, Folio F
    WHERE F.CompanyRecId=1 and D.CompanyRecId=1 and D.DepartCode = F.DepartCode AND D.DepartType = 1 And F.Deleted = 0
      AND F.PostDate >= '20260501' AND F.PostDate <= '20260522'
""")
row = cursor.fetchone()
print("Folio Sum for May 1-22:", float(row[0]))
