# 开发指南

## 环境要求

1. Python 3.9+（skill 运行时仅用标准库，无第三方依赖）
2. Git
3. black（Python 代码格式化，默认 88 列）：提交前运行 `black scripts/ tests/`
4. shfmt（shell 脚本格式化，默认风格）：`*.sh` 改动后运行 `shfmt -w scripts/get_time.sh`
5. pytest（仅测试用）：`pip install pytest`

## 目录结构

```text
Time/
├── SKILL.md            # skill 入口：frontmatter + Agent 使用指引（发布必需）
├── scripts/
│   ├── get_time.py     # 精确路径 CLI 入口：NTP 校时 + 参数解析
│   ├── get_time.sh     # 快速路径：POSIX date 原生取时（Linux/macOS/Git Bash）
│   ├── get_time.ps1    # 快速路径：PowerShell Get-Date 原生取时（Windows）
│   └── timelib/        # Python 精确路径共享库，按职责拆分
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
├── tests/              # 单元测试（不随包发布，可用非标准库）
│   ├── conftest.py        # 导入路径：把 scripts/ 加入 sys.path
│   ├── test_formatting.py
│   ├── test_timezones.py
│   ├── test_sources.py
│   ├── test_native.py     # 快速路径脚本（sh/ps1）集成测试
│   └── test_cli.py
├── README.md           # 项目介绍
├── CHANGELOG.md        # 更新日志
├── VERSION             # 当前版本号（发布时读取第一行）
├── LICENSE             # MIT
├── .github/workflows/  # 发布流水线
├── tag.ps1             # 本地创建并推送版本标签
└── AGENTS.md           # AI 开发约定（禁止修改）
```

## 编码与换行（GBK / UTF-8 注意事项）

1. 所有文本文件一律 UTF-8，换行 LF；例外见 `.gitattributes`：`*.ps1`、`*.bat` 保持 CRLF，且 **`*.ps1` 必须带 UTF-8 BOM**——Windows PowerShell 5.1 对无 BOM 脚本按 ANSI（GBK）解析，中文会乱码甚至语法错误。
2. Windows 管道/重定向下 Python 默认用本地编码（通常 GBK）输出，中文会乱码：脚本入口已调用 `ensure_utf8_stdio()` 强制 UTF-8，新增脚本必须做同样处理。
3. 交互式控制台下 Python 走 Windows 控制台 API（UTF-8），不受 GBK 影响；如仍见乱码，检查终端代码页（`chcp 65001` 切换）。
4. 读写文件时显式指定 `encoding="utf-8"`，不要依赖系统默认编码。

## 本地测试

### 单元测试

```bash
python -m pytest tests/ -v
```

`tests/` 不随包发布（白名单不含该目录），因此测试可用 pytest 等非标准库。除一条对在线/离线都宽容的 CLI 集成用例外，网络逻辑全部 mock，离线可跑。

### 手动验证

```bash
sh scripts/get_time.sh                      # 快速路径（Linux/macOS/Git Bash）
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/get_time.ps1   # 快速路径（Windows）
python scripts/get_time.py                  # 精确路径：网络校时 + 本地时区
python scripts/get_time.py --json           # JSON 输出
python scripts/get_time.py --timezone UTC   # 指定时区
python scripts/get_time.py --local-only     # 本地时钟模式
python scripts/get_time.py --debug          # 查看各校时源失败原因
```

Windows 上 `--timezone` 依赖 `tzdata` 包：`pip install tzdata`。

校时源配置在 `scripts/timelib/sources.py`：`NTP_SERVERS`（UDP 123）、`HTTP_URLS`（HTTPS HEAD 读 Date 头）；本地时钟偏差警告阈值 `CLOCK_WARNING_SECONDS` 在 `scripts/timelib/formatting.py`。沙箱/内网环境 UDP 常被禁，属正常回退路径。

快速路径脚本约束：`get_time.sh` 只用 POSIX strftime 标准格式符（GNU/BSD/BusyBox 通用），单次 `date` 调用取全部字段、少生进程（MSYS 下每个进程创建约 40ms），`LC_ALL=C` 固定英文星期便于映射；输出格式与 `get_time.py` 保持一致，改动需同步更新 `tests/test_native.py`。

## 发布

1. 更新 `VERSION`（如 `v2026.9.2.0`）与 `CHANGELOG.md`。
2. 合并至 `main`，运行 `powershell -File tag.ps1` 创建并推送 `v*` 标签。
3. GitHub Action（`.github/workflows/release.yml`）按白名单打包发布：`SKILL.md`、`scripts/`、`references/`、`README.md`、`CHANGELOG.md`、`LICENSE`、`VERSION`；`DEVELOPMENT.md`、`.github/`、`tag.ps1`、`tests/` 等不会进入发布包。

## 其他约定

1. `AGENTS.md` 为项目最高约定，禁止修改。
2. README.md 面向最终用户，只写功能、使用、安装与环境要求；开发相关内容（本地测试、发布流程、架构约定）一律放本文档——打包时本文档被忽略，README 里的开发链接会成为死链。
3. CLI 入口脚本（`scripts/get_time.py`）只做参数解析与流程编排，可复用的实现放入 `scripts/timelib/`，按职责建模块；新增功能同样入口薄、逻辑下沉。
4. Markdown 统一过 markdownlint，配置见 `.markdownlint.jsonc`。
