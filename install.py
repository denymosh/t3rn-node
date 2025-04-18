#!/bin/bash

# 配置文件和启动项
ENV_FILE="/root/t3rn/executor/executor/bin/.env"
PM2_NAME="t3rn"

# 日志关键词
ERROR_MESSAGE="🔥⛽️ Gas price on L3 is too high & exceeds"
LOG_CLEAR_INTERVAL=3600  # 每小时清空一次日志

# 获取当前Gas设置
get_current_gas_price() {
    grep "^EXECUTOR_MAX_L3_GAS_PRICE=" "$ENV_FILE" | cut -d'=' -f2
}

# 增加Gas并重启程序
increase_gas_and_restart() {
    current_gas=$(get_current_gas_price)
    new_gas=$((current_gas + 50))
    
    echo "⚙️ 检测到Gas过高，正在将Gas价格从 $current_gas 增加到 $new_gas"

    # 修改.env文件
    sed -i "s/^EXECUTOR_MAX_L3_GAS_PRICE=.*/EXECUTOR_MAX_L3_GAS_PRICE=$new_gas/" "$ENV_FILE"

    # 重启程序
    pm2 restart "$PM2_NAME"

    echo "🚀 已将Gas价格设置为 $new_gas 并重启了 $PM2_NAME"
}

# 清空日志
clear_logs() {
    echo "🧹 清空 $PM2_NAME 的日志..."
    pm2 flush
}

# 监控日志
monitor_logs() {
    echo "📡 正在监控 $PM2_NAME 日志..."

    # 定时清空日志
    while true; do
        # 实时监控日志
        pm2 logs "$PM2_NAME" --lines 100 | while read -r line; do
            if echo "$line" | grep -q "$ERROR_MESSAGE"; then
                increase_gas_and_restart
                sleep 5  # 防止频繁重启
            fi
        done

        # 每小时清空一次日志
        sleep "$LOG_CLEAR_INTERVAL"
        clear_logs
    done
}

monitor_logs

