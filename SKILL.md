---
name: time
description: 获取准确的当前时间、日期、星期与 Unix 时间戳，支持指定 IANA 时区显示。当用户询问现在几点、今天日期、星期几、时间戳，或任何任务需要可靠的真实时间（不应依赖模型记忆或猜测）时使用。Get the accurate current time, date, weekday, or Unix timestamp, optionally in a specific timezone. Use for questions like "what time is it" or "what's today's date".
---

# Time

获取准确的当前时间。凡涉及"现在"的事实数据，一律以本脚本输出为准，禁止凭记忆或猜测回答。

## 快速开始

```bash
python scripts/get_time.py
```

脚本会优先通过 NTP 网络校时，失败时自动回退（HTTP Date 头 → 本地时钟），并报告本地时钟偏差。

## 参数

| 参数 | 说明 | 示例 |
|---|---|---|
| `--timezone` | 以指定 IANA 时区显示时间 | `--timezone Asia/Shanghai` |
| `--local-only` | 跳过网络校时，只读本地时钟 | |
| `--json` | 输出 JSON，便于程序化解析 | |
| `--timeout` | 单次网络校时超时秒数（默认 2） | `--timeout 5` |
| `--debug` | 校时失败时向标准错误输出尝试详情 | |

## 输出说明

文本输出示例：

```text
当前时间：2026-09-02 17:05:30 星期三
ISO 8601：2026-09-02T17:05:30.123456+08:00
时区：Asia/Shanghai（UTC+08:00）
UTC：2026-09-02T09:05:30.123456+00:00
Unix 时间戳：1788032730（秒）/ 1788032730123（毫秒）
时间来源：NTP（ntp.aliyun.com），与本地时钟偏差 +0.35 秒
```

`时间来源` 取值及含义：

1. `NTP`：亚秒级精度，以此为准。
2. `HTTP Date`：精度约 1 秒，以此为准。
3. `本地时钟`：网络校时失败时的回退；回答时必须注明"未经网络校准"。

## 使用规则

1. 用户问"现在几点 / 今天日期 / 星期几"：运行脚本，直接引用输出。
2. 用户询问其他时区：加 `--timezone <IANA时区>`（如 `UTC`、`America/New_York`）。
3. 需要程序化处理时间数据：加 `--json`，解析 `iso8601`、`unix_seconds`、`weekday` 等字段。
4. 输出出现 `警告：本地时钟偏差…` 时，说明设备时钟不准，必须采用脚本给出的网络时间，并可提醒用户校准系统时钟。
5. 网络不可用自动回退不算错误；但 `source` 为 `local_clock` 时不得声称时间经过校准。

## 环境要求

1. Python 3.9+，仅标准库，无第三方依赖。
2. Windows 上使用非本地时区（`--timezone`）前需 `pip install tzdata`。
3. 脚本强制 UTF-8 输出，已在 Windows GBK 控制台下处理中文。
