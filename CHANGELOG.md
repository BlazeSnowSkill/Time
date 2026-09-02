# 更新日志

## v2026.9.2-beta.2

1. 新增快速路径：系统原生 `date` / `Get-Date` 命令直接获取本地时间，毫秒级、零依赖
   - `scripts/get_time.sh`（POSIX，Linux / macOS / Git Bash 通用）
   - `scripts/get_time.ps1`（Windows PowerShell，UTF-8 BOM 规避 GBK 乱码）
2. Python 脚本调整为精确路径：NTP 网络校时、时区转换、毫秒时间戳、JSON 结构化
3. SKILL.md 改为双路径决策指引；新增快速路径集成测试 `test_native.py`

## v2026.9.2-beta.1

1. 发布首个版本：`time` skill，获取准确的当前时间
2. 支持网络校时：NTP 优先（亚秒级），HTTP Date 头回退（约 1 秒），本地时钟兜底并报告时钟偏差
3. 支持 `--timezone` 指定 IANA 时区、`--json` 结构化输出、`--local-only` 本地模式、`--debug` 调试
4. 新增 `references/` 排障指南：网络校时、时区、时钟偏差、Python 环境与编码
5. 重构：脚本按职责拆分为 `scripts/timelib/` 包（校时源、时区、渲染、输出编码），CLI 入口与命令行参数保持不变
6. 新增 `tests/` 单元测试（pytest，仅开发依赖、不随包发布）：格式化、时区、校时源（网络逻辑离线 mock）、CLI 集成
