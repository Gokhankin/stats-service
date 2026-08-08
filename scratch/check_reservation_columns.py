import pyodbc
conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute("SELECT TOP 1 * FROM Reservation")
columns = [desc[0] for desc in cursor.description]
print("Columns in Reservation table:")
print(columns)
conn.close()
