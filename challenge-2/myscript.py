#!/usr/bin/env python3
import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
from typing import List, Optional, Tuple


def run_command(cmd: List[str]) -> Tuple[bool, str]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return False, ""
    if result.returncode != 0:
        return False, result.stderr.strip() or result.stdout.strip()
    return True, result.stdout


def bytes_to_human(value: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(value)
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def print_disk_stats() -> None:
    print("\n[disk stats]")
    print(f"{'volume':<25} {'total':>12} {'used':>12} {'free':>12} {'used %':>8}")

    seen = set()
    partitions = [
        "/",
        "/System/Volumes/Data",
        "/System/Volumes/Preboot",
        "/private/var/vm",
    ]

    for mount in partitions:
        if not os.path.exists(mount) or mount in seen:
            continue
        seen.add(mount)
        try:
            usage = shutil.disk_usage(mount)
        except OSError:
            continue
        used_pct = (usage.used / usage.total) * 100 if usage.total else 0.0
        print(
            f"{mount:<25} {bytes_to_human(usage.total):>12} {bytes_to_human(usage.used):>12} "
            f"{bytes_to_human(usage.free):>12} {used_pct:>7.2f}%"
        )


def get_cpu_frequency_hz() -> Optional[int]:
    system = platform.system().lower()
    if system == "darwin":
        ok, out = run_command(["sysctl", "-n", "hw.cpufrequency"])
        if ok:
            try:
                return int(out.strip())
            except ValueError:
                return None
        return None

    if system == "linux":
        try:
            with open("/proc/cpuinfo", "r", encoding="utf-8") as file:
                for line in file:
                    if "cpu MHz" in line:
                        mhz = float(line.split(":", 1)[1].strip())
                        return int(mhz * 1_000_000)
        except (OSError, ValueError):
            return None

    return None


def get_physical_cores() -> Optional[int]:
    system = platform.system().lower()
    if system == "darwin":
        ok, out = run_command(["sysctl", "-n", "hw.physicalcpu"])
        if ok:
            try:
                return int(out.strip())
            except ValueError:
                return None
        return None
    return None


def get_total_cpu_usage() -> Optional[float]:
    system = platform.system().lower()
    if system == "darwin":
        ok, out = run_command(["top", "-l", "1", "-n", "0"])
        if not ok:
            return None
        match = re.search(r"CPU usage:\s*([\d.]+)% user,\s*([\d.]+)% sys", out)
        if not match:
            return None
        return float(match.group(1)) + float(match.group(2))

    if system == "linux":
        ok, out = run_command(["grep", "cpu ", "/proc/stat"])
        if not ok:
            return None
        # Computing deltas needs two samples; keep this simple by using load average fallback.
        try:
            load1, _, _ = os.getloadavg()
            cores = os.cpu_count() or 1
            return min((load1 / cores) * 100, 100.0)
        except OSError:
            return None

    return None


def print_cpu_stats() -> None:
    logical = os.cpu_count() or 0
    physical = get_physical_cores()
    usage = get_total_cpu_usage()
    freq_hz = get_cpu_frequency_hz()

    print("\n[cpu stats]")
    print(f"cores (logical): {logical}")
    print(f"cores (physical): {physical if physical is not None else 'N/A'}")
    print(f"usage: {usage:.2f}%" if usage is not None else "usage: N/A")
    print(f"frequency: {freq_hz / 1_000_000:.2f} MHz" if freq_hz else "frequency: N/A")


def get_ram_stats() -> Optional[Tuple[int, int, int]]:
    system = platform.system().lower()

    if system == "darwin":
        ok_total, out_total = run_command(["sysctl", "-n", "hw.memsize"])
        ok_vm, out_vm = run_command(["vm_stat"])
        if not (ok_total and ok_vm):
            return None

        try:
            total = int(out_total.strip())
            page_size_match = re.search(r"page size of (\d+) bytes", out_vm)
            page_size = int(page_size_match.group(1)) if page_size_match else 4096

            pages = {}
            for line in out_vm.splitlines():
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                value = value.strip().rstrip(".")
                if value.isdigit():
                    pages[key.strip()] = int(value)

            free_pages = pages.get("Pages free", 0) + pages.get("Pages speculative", 0)
            free = free_pages * page_size
            used = max(total - free, 0)
            return total, used, free
        except (ValueError, AttributeError):
            return None

    if system == "linux":
        try:
            mem = {}
            with open("/proc/meminfo", "r", encoding="utf-8") as file:
                for line in file:
                    name, value = line.split(":", 1)
                    mem[name.strip()] = int(value.strip().split()[0]) * 1024

            total = mem.get("MemTotal", 0)
            available = mem.get("MemAvailable", 0)
            used = max(total - available, 0)
            return total, used, available
        except (OSError, ValueError):
            return None

    return None


def print_ram_stats() -> None:
    stats = get_ram_stats()
    print("\n[ram stats]")
    if not stats:
        print("Unable to gather RAM stats on this host.")
        return

    total, used, free = stats
    used_pct = (used / total) * 100 if total else 0.0
    print(f"total: {bytes_to_human(total)}")
    print(f"used: {bytes_to_human(used)}")
    print(f"free: {bytes_to_human(free)}")
    print(f"used percentage: {used_pct:.2f}%")


def parse_port(value: str) -> Optional[int]:
    match = re.search(r":(\d+)$", value)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def collect_listening_ports() -> List[int]:
    ports = set()

    ok, out = run_command(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"])
    if ok:
        for line in out.splitlines()[1:]:
            parts = line.split()
            if len(parts) < 9:
                continue
            name_col = parts[-2]
            port = parse_port(name_col)
            if port is not None:
                ports.add(port)

    if not ports:
        ok, out = run_command(["ss", "-ltn"])
        if ok:
            for line in out.splitlines()[1:]:
                cols = line.split()
                if len(cols) >= 4:
                    port = parse_port(cols[3])
                    if port is not None:
                        ports.add(port)

    if not ports:
        ok, out = run_command(["netstat", "-lnt"])
        if ok:
            for line in out.splitlines():
                cols = line.split()
                if len(cols) < 4:
                    continue
                port = parse_port(cols[3])
                if port is not None:
                    ports.add(port)

    return sorted(ports)


def print_ports_stats() -> None:
    print("\n[ports stats]")
    ports = collect_listening_ports()
    if not ports:
        print("No listening ports found (or required tools are unavailable).")
        return

    print("listening ports:")
    print(", ".join(str(p) for p in ports))


def get_top_processes() -> List[Tuple[str, str, str]]:
    system = platform.system().lower()
    if system == "darwin":
        ok, out = run_command(["ps", "-Ao", "pid,comm,%cpu", "-r"])
    else:
        ok, out = run_command(["ps", "-eo", "pid,comm,%cpu", "--sort=-%cpu"])

    if not ok:
        return []

    rows = []
    for line in out.splitlines()[1:11]:
        parts = line.split(None, 2)
        if len(parts) != 3:
            continue
        rows.append((parts[0], parts[1], parts[2]))
    return rows


def print_overview() -> None:
    print("\n[overview]")
    rows = get_top_processes()
    if not rows:
        print("Unable to gather process overview.")
        return

    print("top 10 process with most CPU usage")
    print(f"{'PID':<10} {'COMMAND':<30} {'CPU %':>8}")
    for pid, command, cpu in rows:
        print(f"{pid:<10} {command:<30} {cpu:>8}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="myscript.py",
        usage="myscript.py [options..]",
        description="Myscript description",
    )
    parser._optionals.title = "Myscript options"

    parser.add_argument("-d", "--disk", action="store_true", help="check disk stats")
    parser.add_argument("-c", "--cpu", action="store_true", help="check cpu stats")
    parser.add_argument("-p", "--ports", action="store_true", help="check listen ports")
    parser.add_argument("-r", "--ram", action="store_true", help="check ram stats")
    parser.add_argument(
        "-o",
        "--overview",
        action="store_true",
        help="top 10 process with most CPU usage.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not any([args.disk, args.cpu, args.ports, args.ram, args.overview]):
        parser.print_help()
        return 0

    if args.disk:
        print_disk_stats()
    if args.cpu:
        print_cpu_stats()
    if args.ports:
        print_ports_stats()
    if args.ram:
        print_ram_stats()
    if args.overview:
        print_overview()

    return 0


if __name__ == "__main__":
    sys.exit(main())#!/usr/bin/env python3
import psutil
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        description='Myscript description',
        usage='myscript.py [options..]'
    )
    parser.add_argument('-d', '--disk', action='store_true', help='check disk stats')
    parser.add_argument('-c', '--cpu', action='store_true', help='check cpu stats')
    parser.add_argument('-p', '--ports', action='store_true', help='check listen ports')
    parser.add_argument('-r', '--ram', action='store_true', help='check ram stats')
    parser.add_argument('-o', '--overview', action='store_true', help='top 10 process with most CPU usage')

    # If no arguments are provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if args.disk:
        print("=== Disk Stats ===")
        for partition in psutil.disk_partitions():
            usage = psutil.disk_usage(partition.mountpoint)
            percent = (usage.used / usage.total) * 100
            print(f"Volume: {partition.device}")
            print(f"  Total: {usage.total / (1024**3):.2f} GB")
            print(f"  Used: {usage.used / (1024**3):.2f} GB")
            print(f"  Free: {usage.free / (1024**3):.2f} GB")
            print(f"  Used Percentage: {percent:.2f}%")

    if args.cpu:
        print("=== CPU Stats ===")
        print(f"Cores: {psutil.cpu_count(logical=True)}")
        print(f"Usage: {psutil.cpu_percent(interval=1)}%")
        freq = psutil.cpu_freq()
        if freq:
            print(f"Frequency: {freq.current:.2f} MHz")

    if args.ram:
        print("=== RAM Stats ===")
        ram = psutil.virtual_memory()
        percent = ram.percent
        print(f"Total: {ram.total / (1024**3):.2f} GB")
        print(f"Used: {ram.used / (1024**3):.2f} GB")
        print(f"Free: {ram.free / (1024**3):.2f} GB")
        print(f"Used Percentage: {percent:.2f}%")

    if args.ports:
        print("=== Listening Ports ===")
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'LISTEN' and conn.laddr:
                print(f"Port {conn.laddr.port} (PID {conn.pid})")

    if args.overview:
        print("=== Top 10 Processes by CPU Usage ===")
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        # Sort by CPU usage descending and get top 10
        for proc in sorted(processes, key=lambda p: p['cpu_percent'] or 0, reverse=True)[:10]:
            print(f"PID: {proc['pid']}, Name: {proc['name']}, CPU: {proc['cpu_percent']}%")

if __name__ == "__main__":
    main()   