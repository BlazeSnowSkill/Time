# -*- coding: utf-8 -*-
"""CLI 入口 get_time.main 的集成测试：本地模式、JSON 输出、错误退出码。"""

import json

from get_time import main


def test_local_only_json(capsys):
    assert main(["--json", "--local-only"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["source"] == "local_clock"
    assert data["fallback_reason"] == "local_only"
    assert data["clock_accurate"] is None


def test_local_only_with_utc_timezone(capsys):
    assert main(["--json", "--local-only", "--timezone", "UTC"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["timezone"] == "UTC"
    assert data["utc_offset"] == "+00:00"


def test_invalid_timezone_exits_with_code_2(capsys):
    assert main(["--json", "--timezone", "Invalid/Zone"]) == 2
    assert "未知时区" in capsys.readouterr().err


def test_json_integration_tolerates_offline(capsys):
    """在线时走 NTP/HTTP，离线回退本地时钟；对两种环境都应成功。"""
    assert main(["--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["source"] in {"ntp", "http", "local_clock"}
    if data["source"] == "local_clock":
        assert data["fallback_reason"] == "network_failed"
    else:
        assert data["fallback_reason"] is None
