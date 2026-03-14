# database/db.py

import aiosqlite
import asyncio
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

from flask import Config

from ..core.models import SystemMetrics


class MetricsDatabase:

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db: aiosqlite.Connection | None = None
        self.db_lock = asyncio.Lock()

    async def init(self):
        """初始化数据库（必须在启动时调用）"""
        self.db = await aiosqlite.connect(self.db_path)
        await self.db.execute("PRAGMA journal_mode=WAL;")

        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                cpu_usage REAL NOT NULL,
                memory_usage REAL NOT NULL,
                disk_usage REAL NOT NULL,
                load_1m REAL DEFAULT -1
            );
        """)

        await self.db.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON metrics (timestamp)"
        )

        await self.db.commit()

    # 插入数据
    async def insert(self, metrics: SystemMetrics, CPU_limit: int, MEM_limit: int):
        timestamp = int(time.time())

        load_1m = metrics.load_1m if metrics.load_1m is not None else -1

        async with self.db_lock:
            await self.db.execute(
                """
                INSERT INTO metrics
                (timestamp, cpu_usage, memory_usage, disk_usage, load_1m)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    metrics.cpu_usage,
                    metrics.memory_usage,
                    metrics.disk_usage,
                    load_1m,
                ),
            )
            await self.db.commit()

    async def get_last_hours(self, data_check_gap: int) -> List[Tuple]:
        """查询最近一段时间的采集数据，并返回给 main.py"""
        cutoff = time.time() - data_check_gap

        async with self.db.execute(
            """
            SELECT timestamp, cpu_usage, memory_usage, disk_usage, load_1m
            FROM metrics
            WHERE timestamp > ?
            ORDER BY timestamp ASC
            """,
            (cutoff,),
        ) as cursor:
            return await cursor.fetchall()

    # 删除旧数据
    async def delete_expired(self, data_del_gap: int):
        timestamp = int(time.time())
        cutoff = timestamp - data_del_gap

        async with self.db_lock:
            await self.db.execute(
                "DELETE FROM metrics WHERE timestamp < ?",
                (cutoff,),
            )
            await self.db.commit()

    async def close(self):
        if self.db:
            await self.db.close()