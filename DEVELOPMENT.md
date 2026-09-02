# 开发指南

## 环境要求

1. Python 3.9+（脚本仅用标准库，无第三方依赖）
2. Git
3. black（Python 代码格式化，默认 88 列）：提交前运行 `black scripts/`

## 目录结构

```text
Time/
├── SKILL.md            # skill 入口：frontmatter + Agent 使用指引（发布必需）
├── scripts/
│   ├── get_time.py     # 获取准确时间的 CLI 入口（参数解析 + 流程编排）
│   └── timelib/        # 共享基础库，按职责拆分
│       ├── __init__.py
│       ├── sources.py     # 校时源：NTP、HTTP Date、回退编排
│       ├── timezones.py   # 时区解析
│       ├── formatting.py  # 结果组装与渲染、偏差告警阈值
│       └── utf8io.py      # UTF-8 输出处理（GBK 规避）
├── references/         # 参考文档（随包发布，按需阅读）
│   └── troubleshooting/
│       ├── network.md
│       ├── timezone.md
│       ├── clock.md
│       └── python.md
├── README.md           # 项目介绍
├── CHANGELOG.md        # 更新日志
├── VERSION             # 当前版本号（发布时读取第一行）
├── LICENSE             # MIT
├── .github/workflows/  # 发布流水线
├── tag.ps1             # 本地创建并推送版本标签
└── AGENTS.md           # AI 开发约定（禁止修改）
```

## 编码与换行（GBK / UTF-8 注意事项）

1. 所有文本文件一律 UTF-8（无 BOM）、LF 换行；`*.ps1`、`*.bat` 例外保持 CRLF，规则见 `.gitattributes`。
2. Windows 管道/重定向下 Python 默认用本地编码（通常 GBK）输出，中文会乱码：脚本入口已调用 `ensure_utf8_stdio()` 强制 UTF-8，新增脚本必须做同样处理。
3. 交互式控制台下 Python 走 Windows 控制台 API（UTF-8），不受 GBK 影响；如仍见乱码，检查终端代码页（`chcp 65001` 切换）。
4. 读写文件时显式指定 `encoding="utf-8"`，不要依赖系统默认编码。

## 本地测试

```bash
python scripts/get_time.py                  # 网络校时 + 本地时区
python scripts/get_time.py --json           # JSON 输出
python scripts/get_time.py --timezone UTC   # 指定时区
python scripts/get_time.py --local-only     # 本地时钟模式
python scripts/get_time.py --debug          # 查看各校时源失败原因
```

Windows 上 `--timezone` 依赖 `tzdata` 包：`pip install tzdata`。

校时源配置在 `scripts/timelib/sources.py`：`NTP_SERVERS`（UDP 123）、`HTTP_URLS`（HTTPS HEAD 读 Date 头）；本地时钟偏差警告阈值 `CLOCK_WARNING_SECONDS` 在 `scripts/timelib/formatting.py`。沙箱/内网环境 UDP 常被禁，属正常回退路径。

## 发布

1. 更新 `VERSION`（如 `v2026.9.2.0`）与 `CHANGELOG.md`。
2. 合并至 `main`，运行 `powershell -File tag.ps1` 创建并推送 `v*` 标签。
3. GitHub Action（`.github/workflows/release.yml`）按白名单打包发布：`SKILL.md`、`scripts/`、`references/`、`README.md`、`CHANGELOG.md`、`LICENSE`、`VERSION`；`.github/`、`tag.ps1` 等不会进入发布包。

## 其他约定

1. `AGENTS.md` 为项目最高约定，禁止修改。
2. CLI 入口脚本（`scripts/get_time.py`）只做参数解析与流程编排，可复用的实现放入 `scripts/timelib/`，按职责建模块；新增功能同样入口薄、逻辑下沉。
3. Markdown 统一过 markdownlint，配置见 `.markdownlint.jsonc`。
