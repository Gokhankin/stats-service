import os
import subprocess

stats_dir = '/home/society/Masaüstü/stats'
os.chdir(stats_dir)

# 1. Remove __pycache__
subprocess.run(['rm', '-rf', '__pycache__', 'templates/__pycache__'])

# 2. Extract clean objects from git commit e9d4964ed
def git_show(path):
    res = subprocess.run(['git', 'show', f'e9d4964ed:{path}'], capture_output=True)
    return res.stdout.decode('utf-8-sig', errors='ignore').replace('\x00', '')

html_text = git_show('templates/index.html')
py_text = git_show('stats_dashboard.py')
queries_text = git_show('queries.py')

# 3. Apply Jinja & layout fixes to index.html
html_text = html_text.replace("all_stats[year]", "all_stats.get(year|string) or all_stats.get(year)")
html_text = html_text.replace("all_stats[2026]", "all_stats.get('2026') or all_stats.get(2026)")
html_text = html_text.replace("all_stats[2025]", "all_stats.get('2025') or all_stats.get(2025)")

target_old_card = 'padding: 18px 24px;'
target_new_card = 'padding: 12px 20px;'
target_old_info = '<div class="metric-info" style="margin-top: 6px; margin-bottom: 0; font-size: 11px; opacity: 0.75; color: #9ca3af; text-align: center;">Bugünün gerçekleşen rakamları ve geçen sene karşılaştırma hedefleri</div>'
target_new_info = '<div class="metric-info" style="margin-top: 2px; margin-bottom: 0; font-size: 10px; opacity: 0.7; color: #9ca3af; text-align: center;">Bugünün gerçekleşen rakamları ve geçen sene karşılaştırma hedefleri</div>'

html_text = html_text.replace(target_old_card, target_new_card, 1)
html_text = html_text.replace(target_old_info, target_new_info)

# 4. Apply pace_stats cache fix to stats_dashboard.py
if '"pace_stats": pace_data' not in py_text and 'res["pace_stats"]' not in py_text:
    py_text = py_text.replace(
        '"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")',
        '"pace_stats": pace_data,\n        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")'
    )

# 5. Apply ISO YYYYMMDD datetime cutoff fix to queries.py
queries_text = queries_text.replace(
    'cutoff = f"{Y}-{month:02d}-{day:02d} 23:59:59"',
    'cutoff = f"{Y}{month:02d}{day:02d} 23:59:59"'
)
queries_text = queries_text.replace("'{year}-{as_of_month_day} 23:59:59'", "'{year}{as_of_month_day.replace(\"-\", \"\")} 23:59:59'")

# 6. Save directly to Linux filesystem
with open('templates/index.html', 'wb') as f:
    f.write(html_text.encode('utf-8'))
with open('stats_dashboard.py', 'wb') as f:
    f.write(py_text.encode('utf-8'))
with open('queries.py', 'wb') as f:
    f.write(queries_text.encode('utf-8'))

print("[+] Clean files saved directly to Linux disk!")
for fn in ['stats_dashboard.py', 'queries.py', 'templates/index.html']:
    with open(fn, 'rb') as f:
        print(f"  {fn} null count:", f.read().count(b'\x00'))
