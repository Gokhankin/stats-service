import pyodbc
import pandas as pd

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
conn = pyodbc.connect(conn_str)

sql = """
SET NOCOUNT ON;
SET DATEFORMAT ymd;
EXEC [dbo].[0103901_AccommodationAnalysis]
    @QRemark            = N'',
    @SalesBegin         = '20000101',
    @SalesEnd           = '20991231',
    @RecordBegin        = '20000101',
    @RecordEnd          = '20991231',
    @CheckinBegin       = '20000101',
    @CheckinEnd         = '20991231',
    @CheckOutBegin      = '20000101',
    @CheckOutEnd        = '20991231',
    @StayBegin          = '20260501',
    @StayEnd            = '20261031',
    @CompanyRecId       = 1,
    @HotelSection       = N'',
    @Agency             = N'',
    @Company            = N'',
    @Source             = N'',
    @Individual         = N'',
    @AgencyGroup        = N'',
    @MainMarket         = N'',
    @SubMarket          = N'',
    @Market             = N'',
    @Nationality        = N'',
    @PriceType          = N'',
    @RoomType           = N'',
    @BedType            = N'',
    @Board              = N'',
    @StayType           = N'',
    @VipType            = N'',
    @PacketType         = N'',
    @GroupNo            = N'',
    @Contract           = N'',
    @Credit             = 0,
    @Repeat             = 0,
    @Code1              = N'',
    @Curr               = N'EUR',
    @WitoutTax          = 1,
    @Department         = N'',
    @OwnerMarket        = 0,
    @OwnerSubMarket     = 0,
    @ExcludeOtherFolios = 1,
    @Channel            = N'',
    @OwnerMainMarket    = 0,
    @OwnerPriceType     = 0,
    @OwnerPType         = N'',
    @OwnerMCode         = N'',
    @OwnerSMCode        = N'',
    @OwnerMMCode        = N''
"""

cursor = conn.cursor()
cursor.execute(sql)

rows = []
while True:
    try:
        col_names = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            rows.append(dict(zip(col_names, row)))
    except Exception:
        pass
    if not cursor.nextset():
        break

df = pd.DataFrame(rows)
df_munferit_tl = df[df['AgencyCode'] == 'MUNFERIT TL']

print("--- MUNFERIT TL totals with wide SP call ---")
print(f"Total TL: {df_munferit_tl['LocalAmount'].sum():,.2f}")
print(f"Total EUR: {df_munferit_tl['RC_NetAmount'].sum():,.2f}")
print(f"Total nights: {df_munferit_tl['RoomNummer'].sum()}")
print(f"Total pax: {df_munferit_tl['Adult'].sum()}")

print("\n--- All agencies wide SP totals ---")
print(f"Grand Total TL: {df['LocalAmount'].sum():,.2f}")
print(f"Grand Total EUR: {df['RC_NetAmount'].sum():,.2f}")

conn.close()
