# -*- coding: utf-8 -*-
"""校时结果的组装与渲染。

build_result 产出的 dict 同时服务文本与 JSON 两种输出形式，
字段结构变更需同步 SKILL.md 的输出说明。
"""

from __future__ import annotations

from datetime import datetime, timezone as dt_timezone

CLOCK_WARNING_SECONDS = 5.0  # 本地时钟偏差超过该值时输出警告
WEEKDAY_NAMES = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")


def format_utc_offset(delta) -> str:
    """把 UTC 偏移量格式化为 +08:00 形式。"""
    total = int(delta.total_seconds())
    sign = "+" if total >= 0 else "-"
    hours, remainder = divmod(abs(total), 3600)
    minutes = remainder // 60
    return f"{sign}{hours:02d}:{minutes:02d}"


def build_result(now_ts: float, tz, source: str, server, local_clock_offset, fallback_reason=None) -> dict:
    """以指定时区渲染时间数据，输出字段同时服务文本与 JSON 两种形式。"""
    dt = datetime.fromtimestamp(now_ts, tz)
    utc = dt.astimezone(dt_timezone.utc)
    zone_name = getattr(tz, "key", None) or dt.tzname() or str(tz)
    iso_week = dt.isocalendar()
    return {
        "source": source,
        "server": server,
        "fallback_reason": fallback_reason,
        "iso8601": dt.isoformat(),
        "timezone": zone_name,
        "utc_offset": format_utc_offset(dt.utcoffset()),
        "date": dt.strftime("%Y-%m-%d"),
        "time": dt.strftime("%H:%M:%S"),
        "weekday": WEEKDAY_NAMES[dt.weekday()],
        "weekday_number": iso_week[2],
        "iso_week": f"{iso_week[0]}-W{iso_week[1]:02d}",
        "unix_seconds": int(now_ts),
        "unix_milliseconds": int(now_ts * 1000),
        "utc": utc.isoformat(),
        "local_clock_offset_seconds": None if local_clock_offset is None else round(local_clock_offset, 3),
        "clock_accurate": None if local_clock_offset is None else abs(local_clock_offset) <= CLOCK_WARNING_SECONDS,
    }


def render_text(result: dict) -> str:
    lines = [
        f"当前时间：{result['date']} {result['time']} {result['weekday']}",
        f"ISO 8601：{result['iso8601']}",
        f"时区：{result['timezone']}（UTC{result['utc_offset']}）",
        f"UTC：{result['utc']}",
        f"Unix 时间戳：{result['unix_seconds']}（秒）/ {result['unix_milliseconds']}（毫秒）",
    ]
    if result["source"] == "local_clock":
        note = "未联网校时" if result["fallback_reason"] == "local_only" else "网络校时失败，未经校准"
        lines.append(f"时间来源：本地时钟（{note}）")
    else:
        offset = result["local_clock_offset_seconds"]
        label = "NTP" if result["source"] == "ntp" else "HTTP Date"
        lines.append(f"时间来源：{label}（{result['server']}），与本地时钟偏差 {offset:+.3f} 秒")
        if not result["clock_accurate"]:
            lines.append(f"警告：本地时钟偏差 {offset:+.3f} 秒，请以上述网络时间为准，并考虑校准系统时钟。")
    return "\n".join(lines)
