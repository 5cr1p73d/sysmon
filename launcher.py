"""
SYSMON Launcher
Starts the FastAPI backend, opens the dashboard in the browser,
and shows a system tray icon for easy access and exit.
"""
import sys, os, socket, threading, time, webbrowser

PORT = 8000

# ── Resource path (works both dev and PyInstaller onefile) ────────────────────
def res(name):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)

# Tell server.py where Dashboard.html is (used by the root "/" route)
os.environ['SYSMON_HTML'] = res('Dashboard.html')

import uvicorn
from server import app

# ── Network helpers ───────────────────────────────────────────────────────────
def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]; s.close(); return ip
    except:
        return '127.0.0.1'

def wait_for_server(timeout=10):
    import urllib.request
    for _ in range(timeout * 10):
        try:
            urllib.request.urlopen(f'http://localhost:{PORT}/', timeout=0.5)
            return True
        except:
            time.sleep(0.1)
    return False

# ── Server thread ─────────────────────────────────────────────────────────────
def run_server():
    uvicorn.run(app, host='0.0.0.0', port=PORT, log_level='warning')

# ── Tray icon ─────────────────────────────────────────────────────────────────
def run_tray(ip):
    try:
        from pystray import Icon, Menu, MenuItem
        from PIL import Image, ImageDraw

        # Generate icon: dark bg + green glow circle
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse([4, 4, size-4, size-4], fill='#050a0e')
        d.ellipse([8, 8, size-8, size-8], fill='#00ff88')
        # Inner dark circle for ring effect
        d.ellipse([18, 18, size-18, size-18], fill='#050a0e')
        # Small center dot
        d.ellipse([26, 26, size-26, size-26], fill='#00ff88')

        def open_local(icon, item):
            webbrowser.open(f'http://localhost:{PORT}')

        def open_network(icon, item):
            webbrowser.open(f'http://{ip}:{PORT}')

        def exit_app(icon, item):
            icon.stop()
            os._exit(0)

        menu = Menu(
            MenuItem('Open Dashboard (local)', open_local, default=True),
            MenuItem(f'Open on network  [{ip}:{PORT}]', open_network),
            MenuItem('Exit', exit_app),
        )

        icon = Icon('SYSMON', img, f'SYSMON  |  {ip}:{PORT}', menu)
        icon.run()

    except ImportError:
        # pystray / Pillow not installed — just keep alive
        print("Tip: install pystray and Pillow for a system tray icon.")
        threading.Event().wait()

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    ip = local_ip()

    print("=" * 44)
    print("  SYSMON")
    print(f"  Local  : http://localhost:{PORT}")
    print(f"  Network: http://{ip}:{PORT}")
    print("=" * 44)

    # Start server in background thread
    threading.Thread(target=run_server, daemon=True).start()

    # Wait until server is up, then open browser
    if wait_for_server():
        webbrowser.open(f'http://localhost:{PORT}')
    else:
        print("Warning: server did not start in time.")

    # System tray (blocks until Exit is clicked)
    run_tray(ip)
