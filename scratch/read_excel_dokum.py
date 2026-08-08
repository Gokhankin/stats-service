import openpyxl
import pandas as pd

excel_path = "/home/society/Masaüstü/Sedna Dashboard/Club Adaköy Rezervasyon Detay Raporu -2026 Sezonu -01.06.2026.xlsx"
wb = openpyxl.load_workbook(excel_path, data_only=True)

sheet = wb['Act Gelir Döküm']
data = []
# Let's read the first 50 rows of this sheet
for r in range(1, 60):
    row_vals = [sheet.cell(row=r, column=c).value for c in range(1, 25)]
    data.append(row_vals)

df = pd.DataFrame(data)
df = df.dropna(how='all', axis=1)
df = df.dropna(how='all', axis=0)

# Print it nicely
print(df.to_string(index=False))

wb.close()
