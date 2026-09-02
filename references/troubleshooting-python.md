# 排障：Python 环境与输出编码

适用症状：`python` 命令找不到、报模块错误、输出中文乱码。

## `python` 不是内部或外部命令

1. Windows 安装 Python 时未勾选 "Add python.exe to PATH"：重新运行安装程序勾选，或改用 `py -3 scripts/get_time.py`。
2. 部分 Linux/macOS 只有 `python3` 命令：改用 `python3 scripts/get_time.py`。

## ModuleNotFoundError: No module named 'zoneinfo'

Python 版本低于 3.9。用 `python --version` 确认后升级，skill 要求 3.9+。

## 输出中文乱码

1. 脚本已强制按 UTF-8 输出，管道/重定向拿到的一定是 UTF-8 字节；乱码说明是读取方按 GBK 解码了。
2. 终端直跑仍乱码：`chcp 65001` 切到 UTF-8 代码页，或改用 Windows Terminal。
3. 二次开发中读写文件一律显式指定 `encoding="utf-8"`，不要依赖系统默认编码（Windows 默认是 GBK）。

## 依赖说明

1. 校时功能零第三方依赖，仅标准库。
2. 唯一例外：Windows 上使用 `--timezone` 需要 `pip install tzdata`，详见时区排障指南。
