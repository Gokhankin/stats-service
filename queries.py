import pandas as pd
import logging
import calendar
from datetime import datetime

log = logging.getLogger(__name__)

# Constants
EXCLUDED_NAMES = "('aaa', 'TOLA', 'test', 'TEST', 'DUMMY')"
AVAILABLE_ROOMS = 111
AVAILABLE_BEDS = 267  # Actual bed capacity of the hotel

def get_exchange_rate(conn):
    try:
        df = pd.read_sql("""
            SELECT TOP 1 ISNULL(NULLIF(Invoice, 0), ISNULL(NULLIF(Pos,0), Buying)) as Rate
            FROM ExchangeRate
            WHERE CurrencyCode = 'EUR'
            ORDER BY CurrDate DESC
        """, conn)
        if not df.empty:
            return float(df.iloc[0]['Rate'])
    except Exception as e:
        log.error(f"Error fetching exchange rate: {e}")
    return 35.0

def get_year_stats(conn, year, as_of_month_day):
    rate = get_exchange_rate(conn)
    
    # NEILSON AGENCY ID
    NEILSON_ID = 1120
    # Monthly Guarantee (35 rooms per day)
    NEILSON_GUARANTEE_PER_DAY = 35
    
    # Common filter for COMP, dummy names, and cancelled reservations
    COMMON_FILTER = f"""
      AND r.Status != -1
      AND ISNULL(a.AgencyCode, '') NOT LIKE '%COMP%'
      AND ISNULL(r.LastName1, '') NOT IN {EXCLUDED_NAMES}
      AND ISNULL(r.FirstName1, '') NOT IN {EXCLUDED_NAMES}
    """

    # Parse date parts
    month = int(as_of_month_day.split('-')[0])
    day = int(as_of_month_day.split('-')[1])
    days_in_month = calendar.monthrange(year, month)[1]
    mtd_days = day  # number of days from 1st to today

    # 1. GENERAL FORECAST MTD: DailyDetail dd.Status=1 — May 1 to today (Season-to-Date for AYLIK DURUM card)
    nights_query = f"""
    SELECT 
        r.AgencyId,
        COUNT(dd.ReservationId) as RoomCount, 
        SUM(r.Pax + r.Childs) as PaxCount,
        SUM(dd.Pax) as BedNightCount
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate BETWEEN '{year}0501' AND '{year}{as_of_month_day.replace("-", "")}'
      AND dd.Status = 1
      {COMMON_FILTER}
    GROUP BY r.AgencyId
    """
    
    try:
        df_nights = pd.read_sql(nights_query, conn)
        night_room = int(df_nights['RoomCount'].sum())
        night_pax = int(df_nights['PaxCount'].sum())
        bed_night = int(df_nights['BedNightCount'].sum())
        
    except Exception as e:
        log.error(f"Error fetching nights for {year}: {e}")
        night_room, night_pax, bed_night = 0, 0, 0

    # LY GENERAL FORECAST MTD (Season-to-Date for AYLIK DURUM card)
    ly_year = year - 1
    ly_nights_query = f"""
    SELECT 
        COUNT(dd.ReservationId) as RoomCount, 
        SUM(r.Pax + r.Childs) as PaxCount,
        SUM(dd.Pax) as BedNightCount
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate BETWEEN '{ly_year}0501' AND '{ly_year}{as_of_month_day.replace("-", "")}'
      AND dd.Status = 1
      {COMMON_FILTER}
    """
    
    try:
        df_ly_nights = pd.read_sql(ly_nights_query, conn)
        ly_night_room = int(df_ly_nights.iloc[0]['RoomCount'] or 0)
        ly_night_pax = int(df_ly_nights.iloc[0]['PaxCount'] or 0)
        ly_bed_night = int(df_ly_nights.iloc[0]['BedNightCount'] or 0)
    except Exception as e:
        log.error(f"Error fetching LY nights for {year}: {e}")
        ly_night_room, ly_night_pax, ly_bed_night = 0, 0, 0

    # 1a. CURRENT MONTH MTD (For Accommodation Analysis Table MTD): StayDate 1st of current month to today
    acc_mtd_query = f"""
    SELECT 
        COUNT(dd.ReservationId) as RoomCount, 
        SUM(dd.Pax) as BedNightCount
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate BETWEEN '{year}{month:02d}01' AND '{year}{as_of_month_day.replace("-", "")}'
      AND dd.Status = 1
      {COMMON_FILTER}
    """
    
    try:
        df_acc_mtd = pd.read_sql(acc_mtd_query, conn)
        acc_mtd_room = int(df_acc_mtd.iloc[0]['RoomCount'] or 0)
        acc_bed_night = int(df_acc_mtd.iloc[0]['BedNightCount'] or 0)
    except Exception as e:
        log.error(f"Error fetching ACC MTD nights for {year}: {e}")
        acc_mtd_room, acc_bed_night = 0, 0

    # LY CURRENT MONTH MTD
    ly_acc_mtd_query = f"""
    SELECT 
        COUNT(dd.ReservationId) as RoomCount, 
        SUM(dd.Pax) as BedNightCount
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate BETWEEN '{ly_year}{month:02d}01' AND '{ly_year}{as_of_month_day.replace("-", "")}'
      AND dd.Status = 1
      {COMMON_FILTER}
    """
    
    try:
        df_ly_acc_mtd = pd.read_sql(ly_acc_mtd_query, conn)
        ly_acc_mtd_room = int(df_ly_acc_mtd.iloc[0]['RoomCount'] or 0)
        ly_acc_bed_night = int(df_ly_acc_mtd.iloc[0]['BedNightCount'] or 0)
    except Exception as e:
        log.error(f"Error fetching LY ACC MTD nights for {year}: {e}")
        ly_acc_mtd_room, ly_acc_bed_night = 0, 0

    # FULL MONTH FORECAST (1st to end of current month)
    fm_query = f"""
    SELECT 
        COUNT(dd.ReservationId) as RoomCount, 
        SUM(dd.Pax) as BedNightCount
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate BETWEEN '{year}{month:02d}01' AND '{year}{month:02d}{days_in_month:02d}'
      AND dd.Status = 1
      {COMMON_FILTER}
    """
    ly_fm_query = f"""
    SELECT 
        COUNT(dd.ReservationId) as RoomCount, 
        SUM(dd.Pax) as BedNightCount
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate BETWEEN '{ly_year}{month:02d}01' AND '{ly_year}{month:02d}{days_in_month:02d}'
      AND dd.Status = 1
      {COMMON_FILTER}
    """
    try:
        df_fm = pd.read_sql(fm_query, conn)
        fm_room = int(df_fm.iloc[0]['RoomCount'] or 0)
        fm_bed_night = int(df_fm.iloc[0]['BedNightCount'] or 0)
    except Exception as e:
        log.error(f"Error fetching full month forecast for {year}: {e}")
        fm_room, fm_bed_night = 0, 0
    try:
        df_ly_fm = pd.read_sql(ly_fm_query, conn)
        ly_fm_room = int(df_ly_fm.iloc[0]['RoomCount'] or 0)
        ly_fm_bed_night = int(df_ly_fm.iloc[0]['BedNightCount'] or 0)
    except Exception as e:
        log.error(f"Error fetching LY full month forecast for {year}: {e}")
        ly_fm_room, ly_fm_bed_night = 0, 0

    # Full month revenue from SP
    fm_sp_date = f"{year}{month:02d}{days_in_month:02d}"
    ly_fm_sp_date = f"{ly_year}{month:02d}{days_in_month:02d}"
    try:
        fm_sql = f"SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='{fm_sp_date}', @AvailableRoom=0"
        df_fm_sp = pd.read_sql(fm_sql, conn)
        fm_rev_eur = float(df_fm_sp.iloc[0].get('MonthlyNetRoomRevenueEUR', 0.0))
    except Exception as e:
        log.error(f"Error fetching full month revenue SP for {year}: {e}")
        fm_rev_eur = 0.0
    try:
        ly_fm_sql = f"SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='{ly_fm_sp_date}', @AvailableRoom=0"
        df_ly_fm_sp = pd.read_sql(ly_fm_sql, conn)
        ly_fm_rev_eur = float(df_ly_fm_sp.iloc[0].get('MonthlyNetRoomRevenueEUR', 0.0))
    except Exception as e:
        log.error(f"Error fetching LY full month revenue SP for {year}: {e}")
        ly_fm_rev_eur = 0.0

    # Calculate Accommodation Analysis metrics
    mtd_avail_rooms = AVAILABLE_ROOMS * mtd_days
    mtd_avail_beds = AVAILABLE_BEDS * mtd_days
    fm_avail_rooms = AVAILABLE_ROOMS * days_in_month
    fm_avail_beds = AVAILABLE_BEDS * days_in_month

    pct_room = (acc_mtd_room / mtd_avail_rooms * 100) if mtd_avail_rooms > 0 else 0
    pct_bed = (acc_bed_night / mtd_avail_beds * 100) if mtd_avail_beds > 0 else 0
    ly_pct_room = (ly_acc_mtd_room / mtd_avail_rooms * 100) if mtd_avail_rooms > 0 else 0
    ly_pct_bed = (ly_acc_bed_night / mtd_avail_beds * 100) if mtd_avail_beds > 0 else 0

    fm_pct_room = (fm_room / fm_avail_rooms * 100) if fm_avail_rooms > 0 else 0
    fm_pct_bed = (fm_bed_night / fm_avail_beds * 100) if fm_avail_beds > 0 else 0
    ly_fm_pct_room = (ly_fm_room / fm_avail_rooms * 100) if fm_avail_rooms > 0 else 0
    ly_fm_pct_bed = (ly_fm_bed_night / fm_avail_beds * 100) if fm_avail_beds > 0 else 0

    # 2. REVENUE (Actuals from ManagerReport SP for Daily/Yearly + Direct Folio for exact MTD match)
    sp_date = f"{year}{as_of_month_day.replace('-', '')}"
    try:
        sql_sp = f"SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='{sp_date}', @AvailableRoom=0"
        df_sp = pd.read_sql(sql_sp, conn)
        
        row = df_sp.iloc[0]
        # Room-only revenue
        total_rev_eur = float(row.get('YearlyNetRoomRevenueEUR', row.get('YearlyRoomRevenueForeign', 0.0)))
        total_rev_try = float(row.get('YearlyNetRoomRevenueLocal', row.get('YearlyRoomRevenue', 0.0)))
        today_rev_eur = float(row.get('DailyNetRoomRevenueEUR', row.get('DailyRoomRevenueForeign', 0.0)))
        today_rev_try = float(row.get('DailyNetRoomRevenueLocal', row.get('DailyRoomRevenue', 0.0)))
    except Exception as e:
        log.error(f"Error fetching revenue SP for {year}: {e}")
        total_rev_eur = total_rev_try = today_rev_eur = today_rev_try = 0.0

    # 2a. Direct Folio Query for MTD exact match (Season-to-Date: May 1st to today, for AYLIK DURUM card)
    folio_query = f"""
    SELECT IsNull(Sum(Case When F.CurrencyCode = 'EUR' Then F.NetAmount Else F.NetAmount*(Dbo.FnFoundCurr(IsNull(F.CurrDate,F.Postdate),F.CurrencyCode,1,1)/Dbo.FnFoundCurr(IsNull(F.CurrDate,F.PostDate),'EUR',1,1)) End),0) As MonthlyRoomRevenueEUR,
           IsNull(Sum(LocalAmount),0) as MonthlyRoomRevenueLocal
    FROM Department D With (NoLock)
    JOIN Folio F With (NoLock) ON D.DepartCode = F.DepartCode AND D.DepartType = 1
    WHERE F.CompanyRecId=1 and D.CompanyRecId=1 And F.Deleted = 0 
      AND F.PostDate BETWEEN '{year}0501' AND '{year}{as_of_month_day.replace("-", "")}'
    """
    try:
        df_fol = pd.read_sql(folio_query, conn)
        monthly_rev_eur = float(df_fol.iloc[0]['MonthlyRoomRevenueEUR'])
        monthly_rev_try = float(df_fol.iloc[0]['MonthlyRoomRevenueLocal'])
    except Exception as e:
        log.error(f"Error fetching exact MTD folio rev for {year}: {e}")
        monthly_rev_eur, monthly_rev_try = 0.0, 0.0

    # 2b. Direct Folio Query for current month MTD exact match (For Accommodation Analysis MTD)
    acc_mtd_folio_query = f"""
    SELECT IsNull(Sum(Case When F.CurrencyCode = 'EUR' Then F.NetAmount Else F.NetAmount*(Dbo.FnFoundCurr(IsNull(F.CurrDate,F.Postdate),F.CurrencyCode,1,1)/Dbo.FnFoundCurr(IsNull(F.CurrDate,F.PostDate),'EUR',1,1)) End),0) As AccMtdRevenueEUR
    FROM Department D With (NoLock)
    JOIN Folio F With (NoLock) ON D.DepartCode = F.DepartCode AND D.DepartType = 1
    WHERE F.CompanyRecId=1 and D.CompanyRecId=1 And F.Deleted = 0 
      AND F.PostDate BETWEEN '{year}{month:02d}01' AND '{year}{as_of_month_day.replace("-", "")}'
    """
    try:
        df_acc_fol = pd.read_sql(acc_mtd_folio_query, conn)
        acc_mtd_rev_eur = float(df_acc_fol.iloc[0]['AccMtdRevenueEUR'])
    except Exception as e:
        log.error(f"Error fetching ACC MTD folio rev for {year}: {e}")
        acc_mtd_rev_eur = 0.0

    # LY REVENUE
    ly_sp_date = f"{ly_year}{as_of_month_day.replace('-', '')}"
    try:
        ly_sql_sp = f"SET NOCOUNT ON; EXEC ManagerReport @CompanyRecID=1, @ManagerDate='{ly_sp_date}', @AvailableRoom=0"
        df_ly_sp = pd.read_sql(ly_sql_sp, conn)
        ly_row = df_ly_sp.iloc[0]
        # LY Room-only revenue
        ly_today_rev_eur = float(ly_row.get('DailyNetRoomRevenueEUR', ly_row.get('DailyRoomRevenueForeign', 0.0)))
    except Exception as e:
        log.error(f"Error fetching LY revenue SP for {year}: {e}")
        ly_today_rev_eur = 0.0

    # LY MTD Exact Match (Season-to-Date: May 1st to today, for AYLIK DURUM card)
    ly_folio_query = f"""
    SELECT IsNull(Sum(Case When F.CurrencyCode = 'EUR' Then F.NetAmount Else F.NetAmount*(Dbo.FnFoundCurr(IsNull(F.CurrDate,F.Postdate),F.CurrencyCode,1,1)/Dbo.FnFoundCurr(IsNull(F.CurrDate,F.PostDate),'EUR',1,1)) End),0) As MonthlyRoomRevenueEUR
    FROM Department D With (NoLock)
    JOIN Folio F With (NoLock) ON D.DepartCode = F.DepartCode AND D.DepartType = 1
    WHERE F.CompanyRecId=1 and D.CompanyRecId=1 And F.Deleted = 0 
      AND F.PostDate BETWEEN '{ly_year}0501' AND '{ly_year}{as_of_month_day.replace("-", "")}'
    """
    try:
        df_ly_fol = pd.read_sql(ly_folio_query, conn)
        ly_monthly_rev_eur = float(df_ly_fol.iloc[0]['MonthlyRoomRevenueEUR'])
    except Exception as e:
        log.error(f"Error fetching exact LY MTD folio rev for {year}: {e}")
        ly_monthly_rev_eur = 0.0

    # LY CURRENT MONTH MTD Exact Match (For Accommodation Analysis MTD)
    ly_acc_mtd_folio_query = f"""
    SELECT IsNull(Sum(Case When F.CurrencyCode = 'EUR' Then F.NetAmount Else F.NetAmount*(Dbo.FnFoundCurr(IsNull(F.CurrDate,F.Postdate),F.CurrencyCode,1,1)/Dbo.FnFoundCurr(IsNull(F.CurrDate,F.PostDate),'EUR',1,1)) End),0) As AccMtdRevenueEUR
    FROM Department D With (NoLock)
    JOIN Folio F With (NoLock) ON D.DepartCode = F.DepartCode AND D.DepartType = 1
    WHERE F.CompanyRecId=1 and D.CompanyRecId=1 And F.Deleted = 0 
      AND F.PostDate BETWEEN '{ly_year}{month:02d}01' AND '{ly_year}{as_of_month_day.replace("-", "")}'
    """
    try:
        df_ly_acc_fol = pd.read_sql(ly_acc_mtd_folio_query, conn)
        ly_acc_mtd_rev_eur = float(df_ly_acc_fol.iloc[0]['AccMtdRevenueEUR'])
    except Exception as e:
        log.error(f"Error fetching LY ACC MTD folio rev for {year}: {e}")
        ly_acc_mtd_rev_eur = 0.0

    # 2c. DAILY ROOMS & PAX — General Forecast for TODAY only
    today_str = f"{year}{as_of_month_day.replace('-', '')}"
    daily_query = f"""
    SELECT 
        COUNT(dd.ReservationId) as DailyRooms,
        ISNULL(SUM(r.Pax + r.Childs), 0) as DailyPax
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate = '{today_str}'
      AND dd.Status = 1
      {COMMON_FILTER}
    """

    # LY Daily: same query for last year's equivalent date
    ly_year = year - 1
    ly_today_str = f"{ly_year}{as_of_month_day.replace('-', '')}"
    ly_daily_query = f"""
    SELECT 
        COUNT(dd.ReservationId) as DailyRooms,
        ISNULL(SUM(r.Pax + r.Childs), 0) as DailyPax
    FROM DailyDetail dd
    JOIN Reservation r ON r.RecId = dd.ReservationId
    LEFT JOIN Agency a ON a.RecId = r.AgencyId
    WHERE dd.StayDate = '{ly_today_str}'
      AND dd.Status = 1
      {COMMON_FILTER}
    """

    try:
        df_daily = pd.read_sql(daily_query, conn)
        daily_rooms = int(df_daily.iloc[0]['DailyRooms'])
        daily_pax = int(df_daily.iloc[0]['DailyPax'])
    except Exception as e:
        log.error(f"Error fetching daily rooms for {year}: {e}")
        daily_rooms, daily_pax = 0, 0

    try:
        df_lydaily = pd.read_sql(ly_daily_query, conn)
        ly_daily_rooms = int(df_lydaily.iloc[0]['DailyRooms'])
        ly_daily_pax = int(df_lydaily.iloc[0]['DailyPax'])
    except Exception as e:
        log.error(f"Error fetching LY daily rooms for {year}: {e}")
        ly_daily_rooms, ly_daily_pax = 0, 0

    # 2d. RESERVATIONS ENTERED TODAY (only for current active year 2026)
    today_entered_rooms = 0
    today_entered_pax = 0
    today_entered_details = []

    if year == 2026:
        today_entered_query = f"""
        SELECT 
            COUNT(DISTINCT r.RecId) as EnteredRooms,
            ISNULL(SUM(r.Pax + r.Childs), 0) as EnteredPax
        FROM Reservation r
        LEFT JOIN Agency a ON a.RecId = r.AgencyId
        WHERE CAST(r.RecordDate AS DATE) = CAST(GETDATE() AS DATE)
          {COMMON_FILTER}
        """

        try:
            df_entpax = pd.read_sql(today_entered_query, conn)
            today_entered_rooms = int(df_entpax.iloc[0]['EnteredRooms'])
            today_entered_pax = int(df_entpax.iloc[0]['EnteredPax'])
        except Exception as e:
            log.error(f"Error fetching today entered for {year}: {e}")
            today_entered_rooms, today_entered_pax = 0, 0

        # Detailed list of reservations entered in the last 14 days with creation date and arrival dates breakdown
        today_entered_detail_query = f"""
        SELECT 
            r.RecId,
            ISNULL(r.Voucher, CAST(r.RecId AS VARCHAR)) as VoucherNo,
            ISNULL(r.FirstName1, '') + ' ' + ISNULL(r.LastName1, '') as GuestName,
            CONVERT(VARCHAR(10), r.CheckinDate, 120) as CheckinDate,
            CONVERT(VARCHAR(10), r.CheckOutDate, 120) as CheckoutDate,
            DATEDIFF(day, r.CheckinDate, r.CheckOutDate) as Nights,
            ISNULL(a.Name, ISNULL(a.AgencyCode, 'MÜNFERİT')) as AgencyName,
            r.Pax,
            r.Childs,
            1 as RoomCount,
            ISNULL(r.RoomType, '') as RoomType,
            CONVERT(VARCHAR(10), r.RecordDate, 120) as RecordDateOnly,
            CONVERT(VARCHAR(16), r.RecordDate, 120) as RecordDate
        FROM Reservation r
        LEFT JOIN Agency a ON a.RecId = r.AgencyId
        WHERE CAST(r.RecordDate AS DATE) >= DATEADD(day, -14, CAST(GETDATE() AS DATE))
          AND YEAR(r.CheckinDate) = {year}
          {COMMON_FILTER}
        ORDER BY r.RecordDate DESC, r.CheckinDate ASC
        """
        try:
            df_entdetails = pd.read_sql(today_entered_detail_query, conn)
            for _, row in df_entdetails.iterrows():
                today_entered_details.append({
                    'RecId': int(row['RecId']),
                    'VoucherNo': str(row['VoucherNo']),
                    'GuestName': str(row['GuestName']),
                    'CheckinDate': str(row['CheckinDate']),
                    'CheckoutDate': str(row['CheckoutDate']),
                    'Nights': int(row['Nights']),
                    'AgencyName': str(row['AgencyName']),
                    'Pax': int(row['Pax']),
                    'Childs': int(row['Childs']),
                    'RoomCount': int(row['RoomCount']),
                    'RoomType': str(row['RoomType']),
                    'RecordDateOnly': str(row['RecordDateOnly']),
                    'RecordDate': str(row['RecordDate'])
                })
        except Exception as e:
            log.error(f"Error fetching today entered details for {year}: {e}")

    # 3. OCCUPANCY (Season Pace - Forecasted rooms vs Capacity)
    try:
        season_start = f"{year}0501"
        season_end = f"{year}1031"
        
        cap_query = f"SELECT COUNT(DISTINCT Room) as RoomCount FROM DailyDetail WHERE StayDate BETWEEN '{season_start}' AND '{season_end}' AND Status != -1"
        df_cap = pd.read_sql(cap_query, conn)
        year_capacity = int(df_cap.iloc[0]['RoomCount'] or 111)
        
        total_season_capacity = year_capacity * 184 # May-Oct

        pace_query = f"""
        SELECT COUNT(*) as SeasonNightRoom
        FROM DailyDetail dd
        JOIN Reservation r ON r.RecId = dd.ReservationId
        LEFT JOIN Agency a ON a.RecId = r.AgencyId
        WHERE dd.StayDate BETWEEN '{season_start}' AND '{season_end}'
          AND dd.Status != -1
          {COMMON_FILTER}
          AND ISNULL(r.RecordDate, r.CheckinDate) <= '{year}{as_of_month_day.replace("-", "")} 23:59:59'
        """
        df_pace = pd.read_sql(pace_query, conn)
        season_rooms = int(df_pace.iloc[0]['SeasonNightRoom'] or 0)
        
        occupancy = (season_rooms / total_season_capacity * 100) if total_season_capacity > 0 else 0
        
    except Exception as e:
        log.error(f"Error calculating occupancy for {year}: {e}")
        occupancy, season_rooms = 0, 0

    # AvpPax = Revenue / BedNight
    avp_pax = (monthly_rev_eur / bed_night) if bed_night > 0 else 0
    ly_avp_pax = (ly_monthly_rev_eur / ly_bed_night) if ly_bed_night > 0 else 0
    
    # Accommodation MTD Average Pax Revenue
    acc_avp_pax = (acc_mtd_rev_eur / acc_bed_night) if acc_bed_night > 0 else 0
    ly_acc_avp_pax = (ly_acc_mtd_rev_eur / ly_acc_bed_night) if ly_acc_bed_night > 0 else 0
    
    fm_avp_pax = (fm_rev_eur / fm_bed_night) if fm_bed_night > 0 else 0
    ly_fm_avp_pax = (ly_fm_rev_eur / ly_fm_bed_night) if ly_fm_bed_night > 0 else 0

    return {
        'NightRoom': night_room,
        'NightPax': night_pax,
        'LYNightRoom': ly_night_room,
        'LYNightPax': ly_night_pax,
        'Occupancy': occupancy,
        'SeasonNightRoom': season_rooms,
        'RevenueEUR': total_rev_eur,
        'RevenueTRY': total_rev_try,
        'MonthlyRevenueEUR': monthly_rev_eur,
        'MonthlyRevenueTRY': monthly_rev_try,
        'LYMonthlyRevenueEUR': ly_monthly_rev_eur,
        'TodayRevenueEUR': today_rev_eur,
        'TodayRevenueTRY': today_rev_try,
        'DailyRooms': daily_rooms,
        'DailyPax': daily_pax,
        'LYDailyRooms': ly_daily_rooms,
        'LYDailyPax': ly_daily_pax,
        'LYTodayRevenueEUR': ly_today_rev_eur,
        'TodayEnteredRooms': today_entered_rooms,
        'TodayEnteredPax': today_entered_pax,
        'TodayEnteredDetails': today_entered_details,
        # Accommodation Analysis (sevki) metrics - MTD
        'PctRoom': pct_room,
        'PctBed': pct_bed,
        'BedNight': acc_bed_night,
        'AvpPax': acc_avp_pax,
        'LYPctRoom': ly_pct_room,
        'LYPctBed': ly_pct_bed,
        'LYBedNight': ly_acc_bed_night,
        'LYAvpPax': ly_acc_avp_pax,
        'AccMtdRevenueEUR': acc_mtd_rev_eur,
        'LYAccMtdRevenueEUR': ly_acc_mtd_rev_eur,
        # Full Month Forecast
        'FMPctRoom': fm_pct_room,
        'FMPctBed': fm_pct_bed,
        'FMBedNight': fm_bed_night,
        'FMRevenueEUR': fm_rev_eur,
        'FMAvpPax': fm_avp_pax,
        'LYFMPctRoom': ly_fm_pct_room,
        'LYFMPctBed': ly_fm_pct_bed,
        'LYFMBedNight': ly_fm_bed_night,
        'LYFMRevenueEUR': ly_fm_rev_eur,
        'LYFMAvpPax': ly_fm_avp_pax,
        'Month': month,
        'Day': day,
        'DaysInMonth': days_in_month,
    }

def get_all_stats(conn, years, as_of_month_day):
    results = {}
    for y in years:
        try:
            results[y] = get_year_stats(conn, y, as_of_month_day)
        except Exception as e:
            log.error(f"Error in get_year_stats for {y}: {e}")
            results[y] = {
                'NightRoom': 0, 'NightPax': 0, 'LYNightRoom': 0, 'LYNightPax': 0,
                'Occupancy': 0.0, 'SeasonNightRoom': 0,
                'RevenueEUR': 0.0, 'RevenueTRY': 0.0,
                'MonthlyRevenueEUR': 0.0, 'MonthlyRevenueTRY': 0.0, 'LYMonthlyRevenueEUR': 0.0,
                'TodayRevenueEUR': 0.0, 'TodayRevenueTRY': 0.0,
                'DailyRooms': 0, 'DailyPax': 0, 'LYDailyRooms': 0, 'LYDailyPax': 0,
                'LYTodayRevenueEUR': 0.0,
                'TodayEnteredRooms': 0, 'TodayEnteredPax': 0, 'TodayEnteredDetails': [],
                'PctRoom': 0, 'PctBed': 0, 'BedNight': 0, 'AvpPax': 0,
                'LYPctRoom': 0, 'LYPctBed': 0, 'LYBedNight': 0, 'LYAvpPax': 0,
                'AccMtdRevenueEUR': 0.0, 'LYAccMtdRevenueEUR': 0.0,
                'FMPctRoom': 0, 'FMPctBed': 0, 'FMBedNight': 0, 'FMRevenueEUR': 0,
                'FMAvpPax': 0, 'LYFMPctRoom': 0, 'LYFMPctBed': 0, 'LYFMBedNight': 0,
                'LYFMRevenueEUR': 0, 'LYFMAvpPax': 0, 'Month': 5, 'Day': 1, 'DaysInMonth': 31,
            }
    return results
