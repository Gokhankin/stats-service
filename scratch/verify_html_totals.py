from bs4 import BeautifulSoup

html_path = "/home/society/Masaüstü/Sedna Dashboard/dashboard_v11.html"
with open(html_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

# Let's search for "TOPLAM (Tüm Board)" in the page text
totals_row = None
for tr in soup.find_all("tr"):
    text = tr.get_text()
    if "TOPLAM (Tüm Board)" in text:
        totals_row = tr
        break

if totals_row:
    tds = [td.get_text().strip() for td in totals_row.find_all(["td", "th"])]
    print("Found totals row:", tds)
else:
    print("Totals row not found!")
