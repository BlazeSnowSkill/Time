# 排障：网络校时失败

适用症状：输出出现 `时间来源：本地时钟（网络校时失败，未经校准）`，或 `--debug` 显示多个校时源失败。

## 快速定位

```bash
python scripts/get_time.py --debug
```

脚本按顺序尝试：5 个 NTP 服务器（UDP 123）→ 3 个 HTTP 站点（HTTPS HEAD 读取 Date 响应头）。`--debug` 会把每次尝试的具体异常打印到标准错误，按第一条报错对症排查。

默认单次超时 2 秒，全部失败最多耗时约 16 秒。已确认离线的环境直接加 `--local-only`，跳过等待。

## NTP 超时：UDP 123 被拦截

1. 报错特征：5 个 NTP 服务器全部 `timed out`。
2. 常见场景：企业内网防火墙、云主机安全组默认禁 UDP、沙箱环境。
3. 处理：
   1. 属预期回退路径：脚本自动转用 HTTP Date 头校时，精度约 1 秒，通常够用。
   2. 弱网环境可放宽超时：`--timeout 5`。
   3. 内网有自建 NTP 服务器时，修改 `scripts/timelib/sources.py` 中的 `NTP_SERVERS`，把内网地址放首位。

## HTTP 校时失败

HTTP 是最后一道网络校时，它也失败才会回退本地时钟。

1. `ProxyError` / `403`：当前网络经代理出网。脚本基于 urllib，自动遵循系统代理与 `HTTP_PROXY` / `HTTPS_PROXY` 环境变量；公司代理可能拦截 HEAD 请求，需检查代理策略。
2. `SSLCertVerificationError`：HTTPS 证书验证失败，多为企业代理做 HTTPS 中间人，需将代理根证书装入系统信任库；不要用关闭证书验证的方式绕过。
3. `getaddrinfo failed`：域名解析失败，DNS 不可用或被限制，按离线场景处理。

## 完全离线

1. 直接使用 `--local-only`，输出会明确标注"未联网校时"。
2. 向用户回答时间时必须说明时间来自本地时钟、未经网络校准。

## 自定义校时源

`NTP_SERVERS`、`HTTP_URLS`、单次超时默认值均在 `scripts/timelib/sources.py` 顶部，可按网络环境调整；修改后至少各验证一次成功路径与回退路径。
