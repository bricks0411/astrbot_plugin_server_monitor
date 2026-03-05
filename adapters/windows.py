# adapters/windows.py

from functools import total_ordering
import os
import time
import psutil
import socket
import platform

from .base import BaseSystemAdapter
from ..core.models import SystemMetrics, HostInfo

class WindowsAdapter(BaseSystemAdapter):
    
    def __init__(self):
        psutil.cpu_percent(interval = None)

    # 获取当前宿主机各项指标
    async def collect(self) -> SystemMetrics:
        # 获取当前时间戳
        timestamp = int(time.time())

        cpu_usage = psutil.cpu_percent(interval = None)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage(os.getenv("SystemDrive", "C:\\")).percent

        return SystemMetrics(
            timestamp    = timestamp,
            cpu_usage    = cpu_usage,
            memory_usage = memory_usage,
            disk_usage   = disk_usage,
            load_1m      = None
        )

    async def get_host_info(self) -> HostInfo:
        hostname = socket.gethostname()

        os_name = platform.system()
        os_version = platform.version()
        architecture = platform.machine()

        cpu_model = platform.processor()
        cpu_physical_cores = psutil.cpu_count(logical = False) or 0
        cpu_logical_cores = psutil.cpu_count(logical = True) or 0

        total_memory = psutil.virtual_memory().total
        total_disk = self._get_total_disk_size()

        return HostInfo(
            hostname           = hostname,
            os_name            = os_name,
            os_version         = os_version,
            architecture       = architecture,
            cpu_model          = cpu_model,
            cpu_physical_cores = cpu_physical_cores,
            cpu_logical_cores  = cpu_logical_cores,
            total_memory       = total_memory,
            total_disk         = total_disk
        )

    def _get_total_disk_size(self):
        total = 0
        for part in psutil.disk_partitions(all = False):
            if 'fixed' in part.opts.lower():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    total += usage.total
                except PermissionError:
                    continue

        return total