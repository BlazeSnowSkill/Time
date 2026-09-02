# -*- coding: utf-8 -*-
"""网络校时源：NTP 优先（亚秒级精度），HTTP Date 响应头回退（约 1 秒精度）。

只依赖标准库。全部服务器失败时 get_network_time 返回 None，
回退策略（本地时钟兜底）由调用方决定。
"""

from __future__ import annotations

import socket
import struct
import sys
import time
import urllib.request
from email.utils import parsedate_to_datetime

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
    request = urllib.request.Request(
        url, method="HEAD", headers={"User-Agent": "time-skill"}
    )
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
