# core/monitor.py

import asyncio
from typing import Optional
from pathlib import Path

from ..adapters.base import BaseSystemAdapter
from .models import SystemMetrics, HostInfo

class ServerMonitorService:

    def __init__(self, adapter: BaseSystemAdapter, data_path: Path):
        self._adapter = adapter

    async def immediate_collect(self) -> SystemMetrics:
        """立即采集宿主机系统指标，不持久化"""
        try:
            return await self._adapter.collect()
        except Exception as e:
            raise RuntimeError(f"Failed to collect metrics: {e}") from e

    async def get_host_info(self) -> HostInfo:
        """获取主机静态信息，详细定义在 core/models.py"""
        try:
            return await self._adapter.get_host_info()
        except Exception as e:
            raise RuntimeError(f"Failed to get host info: {e}") from e