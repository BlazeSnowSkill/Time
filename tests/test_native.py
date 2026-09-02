# -*- coding: utf-8 -*-
"""快速路径集成测试：系统原生 date / Get-Date 脚本的输出格式与时钟一致性。"""

import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WEEKDAYS = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")


def _check_output(text: str) -> None:
    match = re.search(r"当前时间：(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (星期.)", text)
    assert match, f"缺少标准时间行：{text!r}"
    parsed = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
    assert abs((datetime.now() - parsed).total_seconds()) < 30
    # 中文星期必须与日期自洽（验证星期映射表）
    assert match.group(2) == WEEKDAYS[parsed.weekday()]
    assert re.search(
        r"ISO 8601：\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", text
    )
    unix = re.search(r"Unix 时间戳：(\d+)", text)
    assert unix, f"缺少 Unix 时间戳行：{text!r}"
    assert abs(int(unix.group(1)) - time.time()) < 30
    # 本地时钟来源必须声明未经网络校准
    assert "未经网络校准" in text


@pytest.mark.skipif(
    shutil.which("sh") is None, reason="需要 sh（Linux/macOS/Git Bash）"
)
def test_get_time_sh():
    result = subprocess.run(
        ["sh", str(ROOT / "scripts" / "get_time.sh")], capture_output=True, timeout=30
    )
    assert result.returncode == 0
    _check_output(result.stdout.decode("utf-8"))


@pytest.mark.skipif(shutil.which("powershell") is None, reason="需要 powershell")
def test_get_time_ps1():
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ROOT / "scripts" / "get_time.ps1"),
        ],
        capture_output=True,
        timeout=60,
    )
    assert result.returncode == 0
    _check_output(result.stdout.decode("utf-8"))
