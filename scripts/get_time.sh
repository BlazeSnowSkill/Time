#!/bin/sh
# 快速获取本地时间：直接读系统时钟，毫秒级返回，不依赖 Python。
# 仅本地时钟、未经网络校准；需要 NTP 精确时间、时区转换或 JSON，请用同目录 get_time.py。

# 强制英文星期输出，映射不受系统 locale 影响
LC_ALL=C
export LC_ALL

# 一次 date 调用取全部字段（%n 换行分隔；均为 POSIX strftime 标准符，GNU/BSD/BusyBox 通用）
{
	read -r now
	read -r weekday_en
	read -r offset
	read -r unix
	read -r zone
} <<EOF
$(date '+%Y-%m-%d %H:%M:%S%n%A%n%z%n%s%n%Z')
EOF

case "$weekday_en" in
Monday) weekday="星期一" ;;
Tuesday) weekday="星期二" ;;
Wednesday) weekday="星期三" ;;
Thursday) weekday="星期四" ;;
Friday) weekday="星期五" ;;
Saturday) weekday="星期六" ;;
Sunday) weekday="星期日" ;;
*) weekday="$weekday_en" ;;
esac

# %z 形如 +0800，插入冒号变为 +08:00（纯参数展开，避免多起一个进程）
rest=${offset#???}
tz_head=${offset%"$rest"}
tz_colon="$tz_head:$rest"
date_part=${now% *}
time_part=${now#* }

echo "当前时间：$now $weekday"
echo "ISO 8601：${date_part}T${time_part}${tz_colon}"
# MSYS/Git Bash 的 date 可能返回空 %Z
if [ -n "$zone" ]; then
	echo "时区：$zone（UTC$tz_colon）"
else
	echo "时区：UTC$tz_colon"
fi
echo "Unix 时间戳：$unix"
echo "时间来源：本地时钟（date 命令，未经网络校准）"
