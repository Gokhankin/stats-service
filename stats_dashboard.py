import os
import logging
import time
import pyodbc
import json
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
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

DB_SERVER = os.getenv("DB_SERVER", "192.168.0.41,1433")
DB_NAME = os.getenv("DB_NAME", "SednaAdakoy")
DB_USER = os.getenv("DB_USER", "gokhan")
DB_PASS = os.getenv("DB_PASS", "Ad!!2025!!")

CONN_STR = os.getenv(
    "DB_CONNECTION_STRING",
    f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASS};TrustServerCertificate=yes;"
)
PORT = int(os.getenv("PORT", 8085))
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 1800))
YEARS = [2025, 2026]
CACHE_FILE = os.path.join(os.path.dirname(__file__), "stats_cache.json")


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


def load_disk_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log.error(f"Error loading disk cache: {e}")
    return None


def save_disk_cache(data):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.error(f"Error saving disk cache: {e}")


# Global cache + refresh state
cached_data = load_disk_cache()
_refresh_lock = threading.Lock()
_refresh_in_progress = False


def fetch_data():
    global cached_data
    today_str, as_of_date, range_text = get_dates()
    log.info(f"Refreshing seasonal statistics for {as_of_date} from SQL...")
    try:
        conn = get_conn()
        # Fast query: get_all_stats takes ~3 seconds
        all_stats = Q.get_all_stats(conn, YEARS, as_of_date)
        
        current_pace = cached_data.get("pace_stats", {}) if cached_data else {}
        res = {
            "all_stats": all_stats,
            "pace_stats": current_pace,
            "today_str": today_str,
            "range_text": range_text,
            "as_of_date": as_of_date,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        cached_data = res
        save_disk_cache(res)
        
        # Detailed query: get_pace_analysis
        pace_data = Q.get_pace_analysis(conn, as_of_date)
        conn.close()
        
        res["pace_stats"] = pace_data
        cached_data = res
        save_disk_cache(res)
        log.info("Complete refresh finished successfully!")
        return res
    except Exception as e:
        log.error(f"Error fetching data: {e}")
        return None


def trigger_refresh():
    global _refresh_in_progress

    def _do_refresh():
        global _refresh_in_progress
        try:
            fetch_data()
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
    while True:
        time.sleep(REFRESH_INTERVAL)
        trigger_refresh()


def build_html(data):
    if not data:
        return "<h1>Veri yükleniyor, lütfen sayfayı 5 saniye sonra yenileyin...</h1>"
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
    template = env.get_template('index.html')
    all_stats = data.get("all_stats", {})
    pace_stats = data.get("pace_stats", {})
    return template.render(
        all_stats=all_stats,
        pace_stats=pace_stats,
        today_str=data.get("today_str", ""),
        range_text=data.get("range_text", ""),
        updated_at=data.get("updated_at", "")
    )


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global cached_data
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        base_path = parsed.path

        if base_path in ("/", ""):
            if "refresh" in query:
                log.info("Manual refresh requested by user. Triggering refresh in background...")
                trigger_refresh()
            elif cached_data is None:
                trigger_refresh()

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
        pass


def run_server():
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), DashboardHandler) as httpd:
        log.info(f"Statistics Dashboard running at http://localhost:{PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    if not cached_data:
        log.info("Initial cache empty. Performing initial data fetch from SQL...")
        fetch_data()

    threading.Thread(target=update_loop, daemon=True).start()
    run_server()
