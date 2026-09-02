# -*- coding: utf-8 -*-
"""时区解析。

Windows 不自带 IANA 时区数据库，缺 tzdata 包时给出可操作的安装提示。
"""

from __future__ import annotations

import sys
from datetime import timezone as dt_timezone

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9
    ZoneInfo = None


class TimezoneError(Exception):
    """时区名无法解析。"""


def resolve_timezone(name: str):
    """解析 IANA 时区名。Windows 缺少 tzdata 数据时给出可操作的提示。"""
    if name.strip().upper() == "UTC":
        return dt_timezone.utc
    if ZoneInfo is None:
        raise TimezoneError("当前 Python 不含 zoneinfo 模块，请使用 Python 3.9+")
    try:
        return ZoneInfo(name.strip())
    except Exception:
        hint = "，Windows 下请先安装时区数据库：pip install tzdata" if sys.platform == "win32" else ""
        raise TimezoneError(f"未知时区：{name}{hint}") from None
