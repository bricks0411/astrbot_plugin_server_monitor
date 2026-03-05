# main.py
import platform
import time
import asyncio

from .adapters.linux import LinuxAdapter
from .adapters.windows import WindowsAdapter
from .core.monitor import ServerMonitorService
from .database.db import MetricsDatabase
from .utils.chart import draw_server_chart, draw_server_stat_card

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.utils.astrbot_path import get_astrbot_data_path
from pathlib import Path

@register(
    "ServerMonitor", 
    "Bricks0411", 
    "宿主机状态助手，帮每一位开发者获取详细的宿主机信息", 
    "0.0.1"
)
class ServerMonitor(Star):

    def __init__(self, context: Context):
        self.server_system = platform.system()
        # 获取持久化数据存储路径
        base_path = Path(get_astrbot_data_path())
        self.plugin_data_path = base_path / "plugin_data" / self.__class__.__name__
        self.plugin_data_path.mkdir(parents = True, exist_ok = True)

        # 初始化任务时间
        self.last_save_time = 0
        self.last_clean_time = 0

        # 判断系统类型
        if self.server_system == "Windows":
            adapter = WindowsAdapter()
        elif self.server_system in ("Linux", "Darwin"):
            adapter = LinuxAdapter()
        else:
            logger.info(f"未知的系统！{self.server_system}")
            raise RuntimeError("未知系统！")

        self.service = ServerMonitorService(adapter, self.plugin_data_path)
        self.database = MetricsDatabase(self.plugin_data_path / "metric_db.db")

        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        await self.database.init()
        self.collect_task = asyncio.create_task(self.get_server_stat_by_time())
        self.clean_task = asyncio.create_task(self.del_server_stat_by_time())

    @filter.command("查询状态")
    async def check_server_stat(self, event: AstrMessageEvent):
        """查询 bot 宿主机信息 + 状态"""
        metrics = await self.service.immediate_collect()
        host_info = await self.service.get_host_info()
        image_path = str(self.plugin_data_path / "server_image.png")
        draw_server_stat_card(metrics, host_info, image_path)
        yield event.image_result(image_path)

    @filter.command("查询历史")
    async def check_historical_server_stat(self, event: AstrMessageEvent):
        """查询 bot 宿主机历史数据，将其画成折线图并返回"""
        data_get_gap = 3600
        rows = await self.database.get_last_hours(data_get_gap)
        image_path = str(self.plugin_data_path / "server_image.png")
        draw_server_chart(rows, image_path)
        yield event.image_result(image_path)

    async def get_server_stat_by_time(self):
        """按照时间戳获取对应数据，并将数据持久化存储"""
        data_save_gap = 30
        next_run = time.time()
        while True:
            timestamp = time.time()
            # 每隔一段时间便提交一次
            if timestamp >= next_run:
                try:
                    metrics = await self.service.immediate_collect()
                    await self.database.insert(metrics)
                    logger.info(f"数据采集成功！下次采集时间 {timestamp + data_save_gap}")
                except Exception as e:
                    logger.error(f"采集任务失败！")

                self.last_save_time = timestamp
                next_run += data_save_gap

            await asyncio.sleep(max(0, next_run - time.time()))

    async def del_server_stat_by_time(self):
        """按照时间戳删除过旧数据"""
        data_del_gap = 14400
        next_run = time.time()
        while True:
            timestamp = time.time()
            
            if timestamp >= next_run:
                try:
                    await self.database.delete_expired(data_del_gap)
                    logger.info(f"数据清理成功！下次清理时间 {timestamp + data_del_gap}")
                except Exception as e:
                    logger.error(f"清理任务失败！")

                self.last_clean_time = timestamp
                next_run += data_del_gap

            await asyncio.sleep(max(0, next_run - time.time()))

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        if hasattr(self, "collect_task"):
            self.collect_task.cancel()
            try:
                await self.collect_task
            except asyncio.CancelledError:
                pass


        if hasattr(self, "clean_task"):
            self.clean_task.cancel()
            try:
                await self.clean_task
            except asyncio.CancelledError:
                pass

        await self.database.close()
