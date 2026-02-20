"""
core/hardware.py
Detects hardware info cross-platform (Mac, Linux, Windows).
"""

import platform
import subprocess
import psutil


def get_hardware_info() -> dict:
    os_name = platform.system()

    return {
        "os": f"{os_name} {platform.release()}",
        "cpu": _get_cpu(),
        "ram_gb": _get_ram_gb(),
        "gpu": _get_gpu(os_name),
        "arch": platform.machine(),
    }


def _get_cpu() -> str:
    cpu = platform.processor()

    # macOS gives a better result via sysctl
    if platform.system() == "Darwin":
        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

    # Linux: parse /proc/cpuinfo
    if platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
        except Exception:
            pass

    return cpu or "Unknown CPU"


def _get_ram_gb() -> float:
    ram_bytes = psutil.virtual_memory().total
    return round(ram_bytes / (1024 ** 3), 1)


def _get_gpu(os_name: str) -> str:
    """Best-effort GPU detection. Returns 'Unknown' if not found."""

    # macOS: use system_profiler
    if os_name == "Darwin":
        try:
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if "Chipset Model" in line or "Chip" in line:
                    return line.split(":")[1].strip()
        except Exception:
            pass

    # Linux/Windows: try nvidia-smi first (NVIDIA GPUs)
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip().split("\n")[0]
    except Exception:
        pass

    # Linux fallback: lspci
    if os_name == "Linux":
        try:
            result = subprocess.run(
                ["lspci"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if "VGA" in line or "3D" in line:
                    return line.split(":")[-1].strip()
        except Exception:
            pass

    return "Unknown GPU"
