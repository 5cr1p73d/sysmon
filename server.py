"""
PC Monitor Backend — FastAPI + LibreHardwareMonitor (WMI) + psutil
Run as Administrator for full sensor access.

Requirements:
    pip install fastapi uvicorn psutil wmi pythonnet

Usage:
    uvicorn server:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import psutil, json, asyncio, time, platform, os, socket

app = FastAPI(title="PC Monitor API")

def _local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]; s.close(); return ip
    except: return '127.0.0.1'

@app.on_event("startup")
async def _startup():
    ip = _local_ip()
    print(f"\n{'='*44}")
    print(f"  SYSMON")
    print(f"  Local  : http://localhost:8000")
    print(f"  Network: http://{ip}:8000  << smartphone")
    print(f"{'='*44}\n")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── LHM via HTTP web server (port 8085) ─────────────────────────────────────

LHM_URL = "http://localhost:8085/data.json"

def _parse_lhm_value(raw: str):
    """Extract float from LHM value strings like '36,5 °C' or '1282 RPM'."""
    if not raw:
        return None
    try:
        return float(raw.split()[0].replace(",", "."))
    except (ValueError, IndexError):
        return None

def _walk_lhm(node: dict, result: dict):
    """Recursively walk LHM JSON tree, grouping sensors by category."""
    children = node.get("Children", [])
    if not children:
        # Leaf node — parent Text is the category
        return
    # Check if this node's children are leaf sensors (no grandchildren)
    for child in children:
        grandchildren = child.get("Children", [])
        if not grandchildren:
            # child is a leaf sensor; node.Text is the category
            category = node.get("Text", "Unknown")
            val = _parse_lhm_value(child.get("Value", ""))
            if val is not None:
                if category not in result:
                    result[category] = []
                result[category].append({
                    "name":  child["Text"],
                    "value": round(val, 2),
                })
        else:
            _walk_lhm(child, result)

def get_lhm_sensors():
    """Query LibreHardwareMonitor via HTTP API. Returns dict keyed by category."""
    result = {}
    try:
        import urllib.request
        with urllib.request.urlopen(LHM_URL, timeout=1) as r:
            data = json.loads(r.read())
        _walk_lhm(data, result)
    except Exception:
        pass
    return result


# ─── Stats collector ─────────────────────────────────────────────────────────

def get_stats():
    # CPU
    cpu_percent_per_core = psutil.cpu_percent(percpu=True, interval=None)
    cpu_percent = psutil.cpu_percent(interval=None)
    cpu_freq   = psutil.cpu_freq()
    cpu_count  = psutil.cpu_count(logical=True)
    cpu_phys   = psutil.cpu_count(logical=False)

    # Memory
    mem  = psutil.virtual_memory()
    swap = psutil.swap_memory()

    # Disks
    disks = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                "device":    part.device,
                "mountpoint": part.mountpoint,
                "fstype":    part.fstype,
                "total_gb":  round(usage.total  / 1e9, 1),
                "used_gb":   round(usage.used   / 1e9, 1),
                "free_gb":   round(usage.free   / 1e9, 1),
                "percent":   usage.percent,
            })
        except PermissionError:
            pass

    # Network
    net_io = psutil.net_io_counters()

    # LHM sensors (Windows)
    lhm = get_lhm_sensors()

    # Build temperature map: prefer LHM, fall back to psutil
    temps_raw = {}
    if "Temperatures" in lhm:
        for s in lhm["Temperatures"]:
            temps_raw[s["name"]] = s["value"]
    else:
        try:
            for hw, sensors in (psutil.sensors_temperatures() or {}).items():
                for s in sensors:
                    temps_raw[f"{hw} / {s.label or 'sensor'}"] = s.current
        except AttributeError:
            pass  # psutil.sensors_temperatures not available on Windows

    # Wattage / Power from LHM
    power_raw = {}
    for key in ("Powers", "Power"):
        if key in lhm:
            for s in lhm[key]:
                power_raw[s["name"]] = s["value"]
            break

    # GPU load from LHM
    gpu_load = {}
    if "Load" in lhm:
        for s in lhm["Load"]:
            if "gpu" in s["name"].lower():
                gpu_load[s["name"]] = s["value"]

    # Fans from LHM
    fans = {}
    for key in ("Fans", "Fan"):
        if key in lhm:
            for s in lhm[key]:
                fans[s["name"]] = s["value"]
            break

    return {
        "timestamp": time.time(),
        "platform":  platform.node(),
        "os":        f"{platform.system()} {platform.release()}",
        "cpu": {
            "percent":        cpu_percent,
            "per_core":       cpu_percent_per_core,
            "logical_cores":  cpu_count,
            "physical_cores": cpu_phys,
            "freq_mhz":       round(cpu_freq.current) if cpu_freq else 0,
            "freq_max_mhz":   round(cpu_freq.max)     if cpu_freq else 0,
        },
        "memory": {
            "total_gb":  round(mem.total  / 1e9, 2),
            "used_gb":   round(mem.used   / 1e9, 2),
            "avail_gb":  round(mem.available / 1e9, 2),
            "percent":   mem.percent,
            "swap_used_gb":  round(swap.used  / 1e9, 2),
            "swap_total_gb": round(swap.total / 1e9, 2),
            "swap_percent":  swap.percent,
        },
        "disks":       disks,
        "network": {
            "bytes_sent_mb": round(net_io.bytes_sent / 1e6, 1),
            "bytes_recv_mb": round(net_io.bytes_recv / 1e6, 1),
            "packets_sent":  net_io.packets_sent,
            "packets_recv":  net_io.packets_recv,
        },
        "temperatures": temps_raw,
        "power_watts":  power_raw,
        "gpu_load":     gpu_load,
        "fans_rpm":     fans,
        "lhm_available": bool(lhm),
    }


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/stats")
def stats_once():
    return JSONResponse(get_stats())


@app.get("/stream")
async def stats_stream():
    """Server-Sent Events stream — pushes data every second."""
    async def event_generator():
        while True:
            try:
                data = json.dumps(get_stats())
                yield f"data: {data}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/")
def root():
    html = os.environ.get('SYSMON_HTML') or \
           os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Dashboard.html')
    return FileResponse(html, media_type='text/html')