import os, sys, pyodbc, warnings
from dotenv import load_dotenv

sys.path.append("/home/society/Masaüstü/stats")
load_dotenv("/home/society/Masaüstü/stats/.env")
conn = pyodbc.connect(os.getenv("DB_CONNECTION_STRING"))
cursor = conn.cursor()
warnings.filterwarnings("ignore")

# ------------------------------------------------------------------
# A: r.Nights alanıyla — Mayıs 1-20 CheckinDate'e göre
# ------------------------------------------------------------------
print("=== A: SUM(r.Nights) ve SUM(r.Nights * Pax) - CheckinDate May1-20 ===")
for with_comp in [True, False]:
    for statuses in [(1,), (2,3), (1,2,3), (1,2,3,4)]:
        s = ",".join(map(str, statuses))
        comp_filter = "" if with_comp else "AND ISNULL(a.AgencyCode,'') NOT LIKE '%COMP%'"
        q = f"""
            SELECT COUNT(r.RecId), ISNULL(SUM(r.Nights),0), ISNULL(SUM(CAST(r.Nights AS INT) * CAST((r.Pax+r.Childs) AS INT)),0)
            FROM Reservation r
            LEFT JOIN Agency a ON a.RecId = r.AgencyId
            WHERE CAST(r.CheckinDate AS DATE) BETWEEN '20260501' AND '20260520'
              AND r.Status IN ({s})
              {comp_filter}
        """
        try:
            cursor.execute(q)
            row = cursor.fetchone()
            comp_label = "WITH_COMP" if with_comp else "NO_COMP"
            rez, nights, paxnights = row[0] or 0, row[1] or 0, row[2] or 0
            # Print only if any value is close to 1462
            if any(abs(v - 1462) < 50 for v in [rez, nights, paxnights]):
                print(f"  *** CLOSE! Status={statuses} {comp_label}: Rez={rez}, Nights={nights}, PaxNights={paxnights}")
            else:
                print(f"  Status={statuses} {comp_label}: Rez={rez}, Nights={nights}, PaxNights={paxnights}")
        except Exception as e:
            print(f"  ERROR Status={statuses}: {e}")

# ------------------------------------------------------------------
# B: Rezervasyon kesişimi — Mayıs 1-20 boyunca konaklayan tüm rezervasyonlar
# ------------------------------------------------------------------
print("\n=== B: Mayıs 1-20 boyunca konaklayan tüm rezervasyonlar (overlap) ===")
for with_comp in [True, False]:
    for statuses in [(1,), (1,2,3), (1,2,3,4)]:
        s = ",".join(map(str, statuses))
        comp_filter = "" if with_comp else "AND ISNULL(a.AgencyCode,'') NOT LIKE '%COMP%'"
        q = f"""
            SELECT COUNT(DISTINCT r.RecId), ISNULL(SUM(r.Pax+r.Childs), 0), ISNULL(SUM(r.Pax), 0)
            FROM Reservation r
            LEFT JOIN Agency a ON a.RecId = r.AgencyId
            WHERE r.CheckinDate < '20260521' AND r.CheckoutDate > '20260501'
              AND r.Status IN ({s})
              {comp_filter}
        """
        try:
            cursor.execute(q)
            row = cursor.fetchone()
            comp_label = "WITH_COMP" if with_comp else "NO_COMP"
            rez, pax_and_child, pax_only = row[0] or 0, row[1] or 0, row[2] or 0
            if any(abs(v - 1462) < 50 for v in [rez, pax_and_child, pax_only]):
                print(f"  *** CLOSE! Status={statuses} {comp_label}: Rez={rez}, Pax+Childs={pax_and_child}, PaxOnly={pax_only}")
            else:
                print(f"  Status={statuses} {comp_label}: Rez={rez}, Pax+Childs={pax_and_child}, PaxOnly={pax_only}")
        except Exception as e:
            print(f"  ERROR: {e}")

# ------------------------------------------------------------------
# C: NEILSON UNUSED dahil — DailyDetail'de tüm statüler ham sayım
# ------------------------------------------------------------------
print("\n=== C: DailyDetail ham satır sayısı (UNUSED dahil) ===")
cursor.execute("""
    SELECT dd.Status, COUNT(*) as cnt, ISNULL(SUM(r.Pax+r.Childs),0) as pax
    FROM DailyDetail dd
    LEFT JOIN Reservation r ON r.RecId = dd.ReservationId
    WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
    GROUP BY dd.Status
    ORDER BY dd.Status
""")
for row in cursor.fetchall():
    print(f"  dd.Status={row[0]}: Rows={row[1]}, Pax={row[2]}")

# Summary
cursor.execute("""
    SELECT COUNT(*), ISNULL(SUM(r.Pax+r.Childs),0)
    FROM DailyDetail dd
    LEFT JOIN Reservation r ON r.RecId = dd.ReservationId
    WHERE dd.StayDate BETWEEN '20260501' AND '20260520'
""")
row = cursor.fetchone()
print(f"  TÜMÜ (hiç filtre yok): Rows={row[0]}, Pax={row[1]}")

conn.close()
