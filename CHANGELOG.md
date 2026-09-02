# 更新日志

## v2026.9.2.0

1. 发布首个版本：`time` skill，获取准确的当前时间
2. 支持网络校时：NTP 优先（亚秒级），HTTP Date 头回退（约 1 秒），本地时钟兜底并报告时钟偏差
3. 支持 `--timezone` 指定 IANA 时区、`--json` 结构化输出、`--local-only` 本地模式、`--debug` 调试
