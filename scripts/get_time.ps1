# 快速获取本地时间：直接读系统时钟，不依赖 Python。
# 仅本地时钟、未经网络校准；需要 NTP 精确时间、时区转换或 JSON，请用同目录 get_time.py。

# Windows PowerShell 5.1 管道输出默认 GBK，强制 UTF-8 避免中文乱码（PowerShell 7 默认即 UTF-8）
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$now = Get-Date
# [DayOfWeek] 枚举以周日 = 0 起
$weekdayNames = @('星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六')

"当前时间：$($now.ToString('yyyy-MM-dd HH:mm:ss')) $($weekdayNames[[int]$now.DayOfWeek])"
"ISO 8601：$($now.ToString('yyyy-MM-ddTHH:mm:sszzz'))"
"Unix 时间戳：$([DateTimeOffset]::Now.ToUnixTimeSeconds())"
"时间来源：本地时钟（PowerShell Get-Date，未经网络校准）"
