# -*- coding: utf-8 -*-
"""获取准确的当前时间（CLI 入口）。

流程：解析参数 → 解析时区 → 网络校时（失败回退本地时钟）→ 渲染输出。
具体实现拆分在 timelib 包内，见 scripts/timelib/，命令行接口保持稳定。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime

from timelib.formatting import build_result, render_text
from timelib.sources import get_network_time
from timelib.timezones import TimezoneError, resolve_timezone
from timelib.utf8io import ensure_utf8_stdio


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
