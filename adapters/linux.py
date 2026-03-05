# adapters/linux.py

import platform
import socket
import psutil
import os

from .base import BaseSystemAdapter
from ..core.models import SystemMetrics, HostInfo


class LinuxAdapter(BaseSystemAdapter):

    def __init__(self):
        psutil.cpu_percent(interval=None) 

    async def collect(self) -> SystemMetrics:
        import time

        timestamp = int(time.time())

        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent

        load_1m = os.getloadavg()[0]

        return SystemMetrics(
            timestamp    = timestamp,
            cpu_usage    = cpu,
            memory_usage = memory,
            disk_usage   = disk,
            load_1m      = load_1m
        )

    async def get_host_info(self) -> HostInfo:
        hostname = socket.gethostname()

        os_name = platform.system()
        os_version = platform.release()
        architecture = platform.machine()

        cpu_model = self._get_cpu_model()

        cpu_physical = psutil.cpu_count(logical=False) or 0
        cpu_logical = psutil.cpu_count(logical=True) or 0

        total_memory = psutil.virtual_memory().total
        total_disk = self._get_total_disk_size()

        return HostInfo(
            hostname           = hostname,
            os_name            = os_name,
            os_version         = os_version,
            architecture       = architecture,
            cpu_model          = cpu_model,
            cpu_physical_cores = cpu_physical,
            cpu_logical_cores  = cpu_logical,
            total_memory_bytes = total_memory,
            total_disk_bytes   = total_disk
        )

    def _get_cpu_model(self) -> str:
        try:
            with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":", 1)[1].strip()
        except Exception:
            pass
        return "Unknown CPU"

    def _get_total_disk_size(self) -> int:
        total = 0
        for part in psutil.disk_partitions(all=False):
            # 过滤虚拟文件系统
            if part.fstype in ("tmpfs", "devtmpfs", "overlay"):
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                total += usage.total
            except PermissionError:
                continue
        return total