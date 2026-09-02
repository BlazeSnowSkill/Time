# 排障：本地时钟偏差

适用症状：输出出现 `警告：本地时钟偏差 … 秒，请以上述网络时间为准，并考虑校准系统时钟。`

## 警告的含义

1. 数值为「网络时间 − 本地时钟」，偏差超过 5 秒才告警（阈值 `CLOCK_WARNING_SECONDS` 在 `scripts/timelib/formatting.py`）。
2. 此时脚本输出的时间已是校准后的网络时间，可放心引用。
3. 不要再用系统时间命令（`date`、`Get-Date` 等）补充回答，它们读取的是偏差时钟。

## 校准系统时钟

1. Windows（管理员）：`w32tm /resync`；若服务被禁用，先启动 Windows Time 服务。图形界面：设置 → 时间和语言 → 日期和时间 → 立即同步。
2. Linux：`timedatectl set-ntp true` 开启自动同步；chrony 环境可用 `chronyc makestep` 立即对齐。
3. macOS：`sudo sntp -sS time.apple.com`。

## 偏差模式诊断

1. 稳定的小偏差（零点几秒）：正常，NTP 本身是亚秒级精度，无需处理。
2. 固定的秒级偏差：系统时间被手动改过且长期未同步，做一次校准即可。
3. 偏差持续增大：CMOS 电池老化或虚拟机时钟漂移，校准后仍会复发，需换电池或给虚拟机安装时间同步工具。

## 调整告警阈值

`CLOCK_WARNING_SECONDS` 位于 `scripts/timelib/formatting.py` 顶部，调小更严格、调大减少打扰。JSON 输出中对应字段为 `local_clock_offset_seconds` 与 `clock_accurate`，适合程序化判断。
