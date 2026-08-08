import os
import logging
import time
import pyodbc
import threading
import json
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
CONN_STR = os.getenv("DB_CONNECTION_STRING") or os.getenv("CONN_STR") or "DRIVER={ODBC Driver 18 for SQL Server};SERVER=192.168.0.41,1433;DATABASE=SednaAdakoy;UID=gokhan;PWD=Ad!!2025!!;TrustServerCertificate=yes;"
PORT = int(os.getenv("PORT", 8085))
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 1800))
YEARS = [2025, 2026]

CACHE_FILE = os.path.join(os.path.dirname(__file__), 'stats_cache.json')


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


def save_disk_cache(data):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        log.info("Disk cache successfully saved.")
    except Exception as e:
        log.error(f"Error saving disk cache: {e}")


def load_disk_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            log.info("Loaded initial stats from disk cache.")
            return data
        except Exception as e:
            log.error(f"Error loading disk cache: {e}")
    return None


def fetch_data():
    today_str, as_of_date, range_text = get_dates()
    log.info(f"Refreshing seasonal statistics (Pace) for {as_of_date} from SQL...")
    try:
        conn = get_conn()
        data = Q.get_all_stats(conn, YEARS, as_of_date)
        conn.close()
        res = {
            "all_stats": data,
            "today_str": today_str,
            "range_text": range_text,
            "as_of_date": as_of_date,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_disk_cache(res)
        return res
    except Exception as e:
        log.error(f"Error fetching data: {e}")
        return None


# Global cache + refresh state
cached_data = load_disk_cache()
_refresh_lock = threading.Lock()
_refresh_in_progress = False


def trigger_refresh():
    global cached_data, _refresh_in_progress

    def _do_refresh():
        global cached_data, _refresh_in_progress
        try:
            new_data = fetch_data()
            if new_data:
                cached_data = new_data
                log.info("Statistics data successfully updated!")
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
        return """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="3">
    <title>Sedna Stats - Yükleniyor...</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; display: flex; height: 100vh; align-items: center; justify-content: center; margin: 0; }
        .box { text-align: center; background: #1e293b; padding: 2.5rem; border-radius: 1rem; border: 1px solid #334155; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); max-width: 400px; }
        .spinner { border: 4px solid rgba(255,255,255,0.1); width: 44px; height: 44px; border-radius: 50%; border-left-color: #6366f1; animation: spin 0.9s linear infinite; margin: 0 auto 1.25rem; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        h2 { margin: 0 0 0.5rem 0; font-size: 1.25rem; font-weight: 600; color: #fff; }
        p { margin: 0; color: #94a3b8; font-size: 0.875rem; leading-height: 1.5; }
    </style>
</head>
<body>
    <div class="box">
        <div class="spinner"></div>
        <h2>İstatistikler Hazırlanıyor...</h2>
        <p>Sedna veritabanından veri çekiliyor. Sayfa 3 saniye içinde otomatik olarak açılacaktır.</p>
    </div>
    <script>setTimeout(() => location.reload(), 3000);</script>
</body>
</html>"""
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
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
        elif base_path == "/api/today_entered":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            stats_json = cached_data.get("all_stats", {}) if cached_data else {}
            try:
                self.wfile.write(json.dumps(stats_json, ensure_ascii=False).encode("utf-8"))
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
    trigger_refresh()
    threading.Thread(target=update_loop, daemon=True).start()
    run_server()
