# -*- coding: utf-8 -*-
"""timelib.formatting 测试：偏移量格式化、结果组装、文本渲染各分支。"""

from datetime import timedelta, timezone as dt_timezone

import pytest

from timelib.formatting import (
    CLOCK_WARNING_SECONDS,
    build_result,
    format_utc_offset,
    render_text,
)

# 固定基准：2026-09-02 09:00:00 UTC（星期三，ISO 第 36 周）
FIXED_TS = 1788339600.0
UTC = dt_timezone.utc


@pytest.mark.parametrize(
    ("delta", "expected"),
    [
        (timedelta(hours=8), "+08:00"),
        (timedelta(hours=-4), "-04:00"),
        (timedelta(0), "+00:00"),
        (timedelta(hours=5, minutes=30), "+05:30"),
        (timedelta(hours=-9, minutes=-30), "-09:30"),
        (timedelta(hours=5, minutes=30, seconds=45), "+05:30"),  # 秒被丢弃
    ],
)
def test_format_utc_offset(delta, expected):
    assert format_utc_offset(delta) == expected


def test_build_result_fixed_timestamp():
    result = build_result(FIXED_TS, UTC, "ntp", "pool.ntp.org", 0.5)
    assert result["date"] == "2026-09-02"
    assert result["time"] == "09:00:00"
    assert result["weekday"] == "星期三"
    assert result["weekday_number"] == 3
    assert result["iso_week"] == "2026-W36"
    assert result["timezone"] == "UTC"
    assert result["utc_offset"] == "+00:00"
    assert result["unix_seconds"] == 1788339600
    assert result["unix_milliseconds"] == 1788339600000
    assert result["source"] == "ntp"
    assert result["server"] == "pool.ntp.org"
    assert result["fallback_reason"] is None


def test_build_result_offset_rounding():
    result = build_result(FIXED_TS, UTC, "ntp", "s", 1.2344)
    assert result["local_clock_offset_seconds"] == 1.234
    assert result["clock_accurate"] is True


def test_build_result_boundary_offset_is_accurate():
    result = build_result(FIXED_TS, UTC, "ntp", "s", CLOCK_WARNING_SECONDS)
    assert result["clock_accurate"] is True


def test_build_result_large_offset_is_inaccurate():
    result = build_result(FIXED_TS, UTC, "ntp", "s", -6.0)
    assert result["clock_accurate"] is False


def test_build_result_local_clock_fields():
    result = build_result(FIXED_TS, UTC, "local_clock", None, None, "local_only")
    assert result["local_clock_offset_seconds"] is None
    assert result["clock_accurate"] is None
    assert result["fallback_reason"] == "local_only"


def test_render_ntp_accurate_clock_has_no_warning():
    text = render_text(build_result(FIXED_TS, UTC, "ntp", "pool.ntp.org", 0.5))
    assert "NTP（pool.ntp.org）" in text
    assert "+0.500" in text
    assert "警告" not in text


def test_render_ntp_inaccurate_clock_has_warning():
    text = render_text(build_result(FIXED_TS, UTC, "ntp", "pool.ntp.org", 12.34))
    assert "警告：本地时钟偏差 +12.340 秒" in text


def test_render_http_source_label():
    text = render_text(
        build_result(FIXED_TS, UTC, "http", "https://www.baidu.com", 0.3)
    )
    assert "HTTP Date（https://www.baidu.com）" in text


def test_render_local_only_note():
    text = render_text(
        build_result(FIXED_TS, UTC, "local_clock", None, None, "local_only")
    )
    assert "本地时钟（未联网校时）" in text
    assert "偏差" not in text


def test_render_network_failed_note():
    text = render_text(
        build_result(FIXED_TS, UTC, "local_clock", None, None, "network_failed")
    )
    assert "本地时钟（网络校时失败，未经校准）" in text
