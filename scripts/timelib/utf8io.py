# -*- coding: utf-8 -*-
"""标准输入输出编码处理。

Windows 管道/重定向下 Python 默认用本地编码（通常 GBK）输出，中文会乱码；
这里强制按 UTF-8 输出。所有 CLI 入口在解析参数前必须先调用 ensure_utf8_stdio。
"""

import sys


def ensure_utf8_stdio() -> None:
    """把 stdout/stderr 重配置为 UTF-8（管道下默认是 GBK）。"""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass
