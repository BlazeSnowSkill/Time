# 排障：时区问题

适用症状：运行 `--timezone` 报 `错误：未知时区：…`（退出码 2），或对显示的时区名有疑问。

## Windows 报"未知时区"，提示安装 tzdata

1. 原因：Windows 不自带 IANA 时区数据库，Python 的 zoneinfo 找不到数据。
2. 解决：`pip install tzdata`，装一次即可，无需改代码。
3. 验证：

```bash
python -c "from zoneinfo import ZoneInfo; print(ZoneInfo('America/New_York'))"
```

## 时区名称写法

1. 只接受 IANA 名称：`Asia/Shanghai`、`UTC`、`America/New_York`。
2. 不支持 `GMT+8`、`CST`（一词多义）、中文时区名。
3. 查询本机可用的全部时区名：

```bash
python -c "from zoneinfo import available_timezones; print(sorted(available_timezones()))"
```

（同样依赖 tzdata。）

## 默认输出显示"中国标准时间"这类系统名

不传 `--timezone` 时使用系统本地时区，Windows 下显示的是系统时区名（如"中国标准时间"）而非 IANA 名称，属正常现象；需要 IANA 名称时显式传 `--timezone Asia/Shanghai`。

## UTC 特例

`UTC` 由脚本内置支持，任何环境都可用，无需 tzdata。
