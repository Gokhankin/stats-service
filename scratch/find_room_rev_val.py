import os, sys, pyodbc, pandas as pd
from dotenv import load_dotenv
sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
import warnings
warnings.filterwarnings("ignore")

sql = "SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='20260522', @AvailableRoom=0"
df = pd.read_sql(sql, conn)
row = df.iloc[0]
for col in df.columns:
    val = row[col]
    try:
        f_val = float(val)
        if 190000 <= f_val <= 200000:
            print(f"{col}: {f_val}")
    except:
        pass
