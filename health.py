"""S.O.U.L. Agency — PC health sensor. Stdlib only (/proc): $0, shippable.

Pressure score 0-100 (higher = hotter):
  score = 0.5*cpu + 0.3*mem_used + 0.2*load_per_cpu
advice(): max parallel tickets -> 2 normal / 1 warm / 0 critical (pause).
"""
import os
import time


def mem():
    info = {}
    with open("/proc/meminfo") as f:
        for ln in f:
            p = ln.split()
            if p[0] in ("MemTotal:", "MemAvailable:"):
                info[p[0].strip(":")] = int(p[1])  # kB
    total, avail = info["MemTotal"], info["MemAvailable"]
    return {"total_mb": total // 1024, "avail_mb": avail // 1024,
            "used_pct": round(100 * (total - avail) / total, 1)}


def cpu_percent(interval=0.5):
    def read():
        with open("/proc/stat") as f:
            v = list(map(int, f.readline().split()[1:]))
        return v[0] + v[1] + v[2], sum(v)  # busy vs total jiffies
    b1, t1 = read()
    time.sleep(interval)
    b2, t2 = read()
    return round(100 * (b2 - b1) / max(t2 - t1, 1), 1)


def loadavg():
    a, b, c = os.getloadavg()
    n = os.cpu_count() or 1
    return {"1m": round(a, 2), "5m": round(b, 2), "15m": round(c, 2),
            "per_cpu_1m": round(a / n, 2)}


def snapshot():
    m = mem()
    return {"cpu": cpu_percent(), "mem": m, "load": loadavg()}


def score(snap):
    cpu = min(snap["cpu"], 100)
    loadp = min(snap["load"]["per_cpu_1m"] * 100, 100)
    return round(0.5 * cpu + 0.3 * snap["mem"]["used_pct"] + 0.2 * loadp, 1)


def advice(snap=None):
    s = score(snap or snapshot())
    if s >= 85:
        return 0  # critical: pause dispatch, let the laptop breathe
    if s >= 65:
        return 1  # warm: one ticket at a time
    return 2      # normal: two parallel tickets
