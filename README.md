# Time Skill

处理时间相关问题的 Agent Skill。首个功能：获取准确时间——优先 NTP 网络校时，不依赖模型记忆或不可靠的系统时钟。

## 功能

1. **获取准确时间**：NTP 校时（亚秒级精度）→ HTTP Date 头回退（约 1 秒精度）→ 本地时钟兜底，并报告本地时钟偏差。
2. **时区显示**：`--timezone` 指定任意 IANA 时区。
3. **结构化输出**：`--json` 输出 ISO 8601、Unix 时间戳、星期等字段。

## 使用

```bash
# 当前准确时间（本地时区）
python scripts/get_time.py

# 指定时区
python scripts/get_time.py --timezone UTC

# JSON 输出（适合程序解析）
python scripts/get_time.py --json
```

输出示例：

```text
当前时间：2026-09-02 17:05:30 星期三
ISO 8601：2026-09-02T17:05:30.123456+08:00
时区：Asia/Shanghai（UTC+08:00）
UTC：2026-09-02T09:05:30.123456+00:00
Unix 时间戳：1788032730（秒）/ 1788032730123（毫秒）
时间来源：NTP（ntp.aliyun.com），与本地时钟偏差 +0.35 秒
```

## 安装到 Agent

从 [Releases](https://github.com/BlazeSnowSkill/Time/releases) 下载 `Time-Skill-<版本>.zip`，解压后将 `time/` 目录放入你的 Agent 的 skills 目录即可。

## 环境要求

- Python 3.9+，仅标准库，无第三方依赖
- Windows 上使用 `--timezone` 前需 `pip install tzdata`

## 常见问题

排障指南随包附带，见 `references/troubleshooting/`：网络校时失败、时区报错、本地时钟偏差、Python 环境与输出编码。

## License

[MIT](LICENSE)
