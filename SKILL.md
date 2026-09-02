---
name: time
description: 获取准确的当前时间、日期、星期与 Unix 时间戳，支持指定 IANA 时区显示。当用户询问现在几点、今天日期、星期几、时间戳，或任何任务需要可靠的真实时间（不应依赖模型记忆或猜测）时使用。Get the accurate current time, date, weekday, or Unix timestamp, optionally in a specific timezone. Use for questions like "what time is it" or "what's today's date".
---

# Time

获取当前时间。默认走快速路径——系统原生命令直接读时钟，毫秒级返回；需要网络校时、时区转换或结构化数据时走精确路径——Python 脚本 + NTP。

## 路径一：快速获取（默认首选）

回答"现在几点 / 今天日期 / 星期几 / Unix 秒级时间戳"时使用，零依赖：

```bash
# Linux / macOS / Windows（Git Bash）
sh scripts/get_time.sh
```

```powershell
# Windows PowerShell（无 sh 环境时）
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/get_time.ps1
```

输出示例（两个脚本格式一致）：

```text
当前时间：2026-09-02 17:58:40 星期三
ISO 8601：2026-09-02T17:58:40+08:00
时区：UTC+08:00
Unix 时间戳：1788343120
时间来源：本地时钟（date 命令，未经网络校准）
```

## 路径二：精确获取（按需）

具备以下任一需求时改用 Python 脚本：

1. **网络校时**：NTP 优先（亚秒级精度），HTTP Date 头回退，并报告本地时钟偏差
2. **时区转换**：`--timezone <IANA时区>`（如 `UTC`、`America/New_York`）
3. **结构化数据**：`--json`（ISO 周、毫秒时间戳、程序可解析字段）
4. 其余参数：`--local-only`（跳过联网）、`--timeout`（单次校时超时）、`--debug`（输出失败详情）

```bash
python scripts/get_time.py            # 网络校时 + 本地时区
python scripts/get_time.py --json     # JSON 输出
```

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

## 路径选择规则

1. 日常询问"现在几点 / 今天日期"：走路径一，直接引用输出。
2. 快速路径输出已注明"未经网络校准"，回答时不得声称时间经过网络校准。
3. 任务对时间准确性敏感（秒级对账、签名校验、日志时序），或用户明确要求"准确/网络时间"：走路径二。
4. 时区转换、毫秒时间戳、ISO 周、JSON：走路径二。
5. 用户质疑本地时钟不准：直接走路径二，以其网络时间为准，并参考时钟偏差警告。

## 排障

遇到异常先看输出与退出码，再按类别读取 `references/troubleshooting/` 下对应的指南：

| 症状 | 指南 |
|---|---|
| 时间来源回退为本地时钟、NTP/HTTP 校时失败 | `references/troubleshooting/network.md` |
| 时区报错、时区名不识别 | `references/troubleshooting/timezone.md` |
| 出现"本地时钟偏差"警告 | `references/troubleshooting/clock.md` |
| `python` 命令找不到、版本过低、中文乱码 | `references/troubleshooting/python.md` |

## 环境要求

1. 快速路径：零依赖，任何 Linux / macOS / Windows 均可（sh 或 PowerShell 任一）。
2. 精确路径：Python 3.9+，仅标准库；Windows 上使用非本地时区（`--timezone`）前需 `pip install tzdata`。
3. 所有脚本强制 UTF-8 输出，已在 Windows GBK 控制台下处理中文。
