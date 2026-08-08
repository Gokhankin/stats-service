import openpyxl
import pandas as pd

excel_path = "/home/society/Masaüstü/Sedna Dashboard/Club Adaköy Rezervasyon Detay Raporu -2026 Sezonu -01.06.2026.xlsx"
wb = openpyxl.load_workbook(excel_path, data_only=True)

def inspect_sheet(sheet_name):
    sheet = wb[sheet_name]
    data = []
    # Read rows up to row 40
    for r in range(1, 40):
        row_vals = [sheet.cell(row=r, column=c).value for c in range(1, 20)]
        data.append(row_vals)
    df = pd.DataFrame(data)
    # Drop completely empty columns
    df = df.dropna(how='all', axis=1)
    # Drop completely empty rows
    df = df.dropna(how='all', axis=0)
    print(f"\n--- Sheet: {sheet_name} ---")
    print(df.to_string(index=False))

inspect_sheet('Act Gelir Döküm')
inspect_sheet('Act Gelir Board Dökümlü')

wb.close()
