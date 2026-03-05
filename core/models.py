# core/models.py

from dataclasses import dataclass

@dataclass(slots = True)
class SystemMetrics:
    timestamp: int
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    load_1m: float | None               # 系统在 1 分钟内的平均负载

@dataclass(slots = True)
class HostInfo:
    hostname: str
    os_name: str
    os_version: str
    architecture: str                   # 系统架构

    cpu_model: str
    cpu_physical_cores: int             # CPU 物理核心
    cpu_logical_cores: int              # CPU 逻辑核心

    total_memory_bytes: int | None
    total_disk_bytes: int | None