import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;')
cursor = conn.cursor()
for y in [2024, 2025, 2026]:
    cursor.execute(f"SELECT COUNT(*) FROM DailyDetail WHERE StayDate BETWEEN '{y}0501' AND '{y}1031' AND Status != -1")
    count = cursor.fetchone()[0]
    print(f"{y} Season Total: {count}")
    
    cursor.execute(f"SELECT COUNT(DISTINCT Room) FROM DailyDetail WHERE StayDate BETWEEN '{y}0501' AND '{y}1031' AND Status != -1")
    distinct_rooms = cursor.fetchone()[0]
    print(f"{y} Distinct Rooms: {distinct_rooms}")
    
    # Check full year
    cursor.execute(f"SELECT COUNT(*) FROM DailyDetail WHERE YEAR(StayDate) = {y} AND Status != -1")
    full_year = cursor.fetchone()[0]
    print(f"{y} Full Year Total: {full_year}")
