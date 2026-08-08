import os
import logging
import time
import pyodbc
import threading
from datetime import datetime
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
import http.server
import socketserver
import queries as Q

# Setup Logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

# Load Environment
load_dotenv()
CONN_STR = os.getenv("DB_CONNECTION_STRING")
PORT = int(os.getenv("PORT", 8085))
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 1800))
YEARS = [2025, 2026]


def get_dates():
    now = datetime.now()
    months = {
        1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN",
        7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"
    }
    today_str = f"{now.day} {months[now.month]} {now.year}"
    as_of_date = now.strftime("%m-%d")
    range_text = f"1 MAYIS - {now.day} {months[now.month]}"
    return today_str, as_of_date, range_text


def get_conn():
    return pyodbc.connect(CONN_STR, timeout=30)


def fetch_data():
    today_str, as_of_date, range_text = get_dates()
    log.info(f"Refreshing seasonal statistics (Pace) for {as_of_date} from SQL...")
    try:
        conn = get_conn()
        data = Q.get_all_stats(conn, YEARS, as_of_date)
        conn.close()
        return {
            "all_stats": data,
            "today_date": today_str,
            "range_text": range_text,
            "last_update": datetime.now().strftime("%H:%M:%S")
        }
    except Exception as e:
        log.error(f"Error fetching data: {e}")
        return None


# Global cache + refresh state
cached_data = None
_refresh_lock = threading.Lock()
_refresh_in_progress = False


def trigger_refresh():
    """
    Arkaplanda (non-blocking) refresh başlatır.
    Zaten devam eden bir refresh varsa ikincisini başlatmaz.
    """
    global cached_data, _refresh_in_progress

    def _do_refresh():
        global cached_data, _refresh_in_progress
        try:
            data = fetch_data()
            if data:
                cached_data = data
        finally:
            with _refresh_lock:
                _refresh_in_progress = False

    with _refresh_lock:
        if _refresh_in_progress:
            log.info("Refresh already in progress, skipping duplicate request.")
            return False
        _refresh_in_progress = True

    threading.Thread(target=_do_refresh, daemon=True).start()
    return True


def update_loop():
    """Periyodik otomatik güncelleme döngüsü — her REFRESH_INTERVAL saniyede bir."""
    while True:
        time.sleep(REFRESH_INTERVAL)
        trigger_refresh()


def build_html(data):
    if not data:
        return "<h1>Veri yukleniyor, lutfen bekleyin...</h1>"
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('index.html')
    return template.render(**data)


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        base_path = parsed.path

        if base_path in ("/", ""):
            if "refresh" in query:
                # Non-blocking: refresh arkaplanda başlar, cache'deki mevcut veri hemen döner
                if trigger_refresh():
                    log.info("Manual refresh triggered in background.")

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            html = build_html(cached_data)
            try:
                self.wfile.write(html.encode("utf-8"))
            except BrokenPipeError:
                pass
        else:
            try:
                super().do_GET()
            except BrokenPipeError:
                pass

    def log_message(self, format, *args):
        # Request spam'ı bastır, sadece önemli loglar görünsün
        pass


def run_server():
    # ThreadingTCPServer: Her HTTP isteği ayrı thread'de işlenir
    # Böylece arkaplandaki SQL refresh sunucuyu asla bloke edemez
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), DashboardHandler) as httpd:
        log.info(f"Statistics Dashboard running at http://localhost:{PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    # İlk veri yüklemesi senkron (sunucu başlamadan önce veri hazır olsun)
    cached_data = fetch_data()

    # Periyodik güncelleme thread'i
    threading.Thread(target=update_loop, daemon=True).start()

    # Sunucu başlat (ThreadingTCPServer — non-blocking)
    run_server()
