# adapters/base.py

from abc import ABC, abstractmethod
from ..core.models import SystemMetrics, HostInfo

class BaseSystemAdapter(ABC):
    
    @abstractmethod
    async def collect(self) -> SystemMetrics:
        raise NotImplementedError

    @abstractmethod
    async def get_host_info(self) -> HostInfo:
        raise NotImplementedError

    async def initialize(self) -> None:
        pass

    async def close(self) -> None:
        pass