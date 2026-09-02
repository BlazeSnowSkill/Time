# -*- coding: utf-8 -*-
"""timelib.timezones 测试：UTC 特例、IANA 名称、无效名称报错。"""

import sys
from datetime import timezone as dt_timezone
from zoneinfo import ZoneInfo

import pytest

from timelib.timezones import TimezoneError, resolve_timezone


def _have_tzdata() -> bool:
    try:
        ZoneInfo("Asia/Shanghai")
        return True
    except Exception:
        return False


def test_utc_builtin():
    assert resolve_timezone("UTC") is dt_timezone.utc


def test_utc_case_and_whitespace_insensitive():
    assert resolve_timezone(" utc ") is dt_timezone.utc


@pytest.mark.skipif(
    not _have_tzdata(), reason="需要 tzdata（Windows：pip install tzdata）"
)
def test_iana_name():
    assert getattr(resolve_timezone("Asia/Shanghai"), "key") == "Asia/Shanghai"


def test_invalid_name_raises():
    with pytest.raises(TimezoneError, match="未知时区"):
        resolve_timezone("Invalid/Zone")


@pytest.mark.skipif(sys.platform != "win32", reason="tzdata 安装提示仅 Windows 给出")
def test_invalid_name_hints_tzdata_on_windows():
    with pytest.raises(TimezoneError, match="pip install tzdata"):
        resolve_timezone("Invalid/Zone")
