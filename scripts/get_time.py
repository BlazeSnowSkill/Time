# -*- coding: utf-8 -*-
"""获取准确的当前时间。

校时优先级：NTP（亚秒级精度）→ HTTP Date 响应头（约 1 秒精度）→ 本地时钟（回退）。
只依赖 Python 标准库，网络全部失败时仍可用，但会在输出中标注时间来源。
"""

from __future__ import annotations

import argparse
import json
import socket
import struct
import sys
import time
import urllib.request
from datetime import datetime, timezone as dt_timezone
from email.utils import parsedate_to_datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9
    ZoneInfo = None

NTP_EPOCH_DELTA = 2208988800  # 1900-01-01 与 1970-01-01 之间的秒数
NTP_PORT = 123
NTP_SERVERS = (
    "ntp.aliyun.com",
    "ntp.tencent.com",
    "cn.ntp.org.cn",
    "pool.ntp.org",
    "time.cloudflare.com",
)
HTTP_URLS = (
    "https://www.baidu.com",
    "https://www.cloudflare.com",
    "https://www.microsoft.com",
)
CLOCK_WARNING_SECONDS = 5.0  # 本地时钟偏差超过该值时输出警告

WEEKDAY_NAMES = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")


class TimezoneError(Exception):
    """时区名无法解析。"""


def ensure_utf8_stdio() -> None:
    """Windows 管道默认编码可能是 GBK，强制按 UTF-8 输出，避免中文乱码。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


def ntp_offset(host: str, timeout: float) -> float:
    """查询 NTP 服务器，返回「网络时间 - 本地时钟」的偏移秒数。失败时抛出异常。"""
    packet = bytearray(48)
    packet[0] = 0x23  # LI=0, VN=4, Mode=3（客户端）
    t0 = time.time()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        sock.sendto(bytes(packet), (host, NTP_PORT))
        data, _ = sock.recvfrom(48)
    t3 = time.time()
    if len(data) < 48 or data[1] == 0:
        raise ValueError("NTP 响应无效（stratum 为 0）")
    t1 = _ntp_to_unix(data[32:40])  # 服务器接收时刻
    t2 = _ntp_to_unix(data[40:48])  # 服务器发送时刻
    offset = ((t1 - t0) + (t2 - t3)) / 2
    if abs(offset) > 10 * 366 * 86400:
        raise ValueError("NTP 偏差异常，拒绝采信")
    return offset


def _ntp_to_unix(raw: bytes) -> float:
    """NTP 64 位时间戳（自 1900 年起的秒数 + 小数部分）转 Unix 时间戳。"""
    secs, frac = struct.unpack("!II", raw)
    return secs - NTP_EPOCH_DELTA + frac / 2**32


def http_offset(url: str, timeout: float) -> float:
    """用 HTTP 响应头 Date 校时，返回偏移秒数。精度受 Date 秒级分辨率限制。"""
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "time-skill"})
    start = time.time()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        date_header = response.headers.get("Date")
    rtt = time.time() - start
    if not date_header:
        raise ValueError("响应缺少 Date 头")
    server_ts = parsedate_to_datetime(date_header).timestamp()
    # Date 头只精确到秒，用单程近似（RTT 的一半）补偿传输耗时
    return (server_ts + rtt / 2) - start


def get_network_time(timeout: float, debug: bool = False):
    """依次尝试 NTP 与 HTTP 校时。返回 (偏移秒数, 来源, 服务器)，全部失败返回 None。"""
    for host in NTP_SERVERS:
        try:
            return ntp_offset(host, timeout), "ntp", host
        except Exception as exc:
            if debug:
                print(f"[debug] NTP {host} 失败：{exc}", file=sys.stderr)
    for url in HTTP_URLS:
        try:
            return http_offset(url, timeout), "http", url
        except Exception as exc:
            if debug:
                print(f"[debug] HTTP {url} 失败：{exc}", file=sys.stderr)
    return None


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


def main(argv=None) -> int:
    ensure_utf8_stdio()
    parser = argparse.ArgumentParser(description="获取准确的当前时间（优先 NTP 网络校时）")
    parser.add_argument("--timezone", metavar="IANA时区", help="以指定 IANA 时区显示，如 Asia/Shanghai、UTC；默认为系统本地时区")
    parser.add_argument("--local-only", action="store_true", help="跳过网络校时，仅使用本地时钟")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    parser.add_argument("--timeout", type=float, default=2.0, help="单次网络校时超时秒数（默认 2）")
    parser.add_argument("--debug", action="store_true", help="校时失败时向标准错误输出各次尝试详情")
    args = parser.parse_args(argv)

    try:
        tz = resolve_timezone(args.timezone) if args.timezone else datetime.now().astimezone().tzinfo
    except TimezoneError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2

    source, server, local_clock_offset, fallback_reason = "local_clock", None, None, None
    if args.local_only:
        fallback_reason = "local_only"
    else:
        network = get_network_time(args.timeout, args.debug)
        if network is None:
            fallback_reason = "network_failed"
        else:
            local_clock_offset, source, server = network
    now_ts = time.time() + (local_clock_offset if local_clock_offset is not None else 0.0)

    result = build_result(now_ts, tz, source, server, local_clock_offset, fallback_reason)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
