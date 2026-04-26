# SYSMON

Real-time PC monitoring dashboard. View CPU, RAM, disk, network, temperatures, fan speeds and power consumption from any browser on your local network — including smartphone.

> **Windows only** · No installation required · Run as Administrator for full sensor access

---

## Download

Grab the latest release from the [Releases](../../releases/latest) page — no Python needed.

| File | Description |
|------|-------------|
| `SYSMON.exe` | Portable single-file executable |
| `SYSMON_Setup.exe` | Windows installer |

---

## Features

- **Live graphs** — CPU, RAM, disk I/O, network throughput
- **Hardware sensors** — temperatures, fan RPM, power draw (via LibreHardwareMonitor)
- **Favorites page** — pin any widget or individual sensor, drag and resize freely
- **Two resize modes** — resize container only, or scale content (text + icons scale too)
- **Settings panel** — theme presets, custom colors, snap grid, lock layout, scanlines
- **Fullscreen** — works on PC and smartphone in landscape/portrait
- **Persistent** — layout and settings survive restarts
- **Network access** — open the dashboard from any device on the same Wi-Fi

---

## Quick Start

1. Download `SYSMON.exe` from [Releases](../../releases/latest)
2. Right-click → **Run as Administrator**
3. Dashboard opens in your browser automatically
4. A tray icon appears — right-click for options

**From smartphone or another device:**
```
http://<your-pc-ip>:8000
```
The exact URL is shown in the tray icon tooltip and in the console on startup.

---

## Optional: Hardware Sensors (temperatures, fans, watts)

SYSMON reads hardware sensors from [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases) via its built-in web server.

1. Download and run LibreHardwareMonitor **as Administrator**
2. Enable: `Options → Web Server → Run Web Server` (port 8085)
3. Leave it running in the system tray — SYSMON picks it up automatically

Without LHM: CPU load, RAM, disk, and network still work normally.

---

## Ports

| Port | Service |
|------|---------|
| 8000 | SYSMON web server |
| 8085 | LibreHardwareMonitor (optional, run separately) |

---

## Building from Source

Requirements: Python 3.x, pip

```bat
build.bat
```

Output: `dist\SYSMON.exe`

For the Windows installer (`SYSMON_Setup.exe`): install [Inno Setup 6](https://jrsoftware.org/isinfo.php) then compile `installer.iss`.

**Stack:** Python · FastAPI · uvicorn · psutil · pystray · PyInstaller

---

## License

MIT
