#!/bin/bash

# * put `run_gpu_monitor_otlp.py` in the same folder as this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# provide dns
DNS_TO_ADD="nameserver 10.205.248.11"
RESOLV_CONF="/etc/resolv.conf"

if grep -qF "$DNS_TO_ADD" "$RESOLV_CONF"; then
    echo "'$DNS_TO_ADD' already exists. No changes needed."
else
    echo "Adding '$DNS_TO_ADD' to $RESOLV_CONF."

    TMP_FILE=$(mktemp)
    echo "$DNS_TO_ADD" > "$TMP_FILE"
    cat "$RESOLV_CONF" >> "$TMP_FILE"
    cat "$TMP_FILE" > "$RESOLV_CONF"
    rm "$TMP_FILE"

    echo "$RESOLV_CONF has been updated:"
    cat "$RESOLV_CONF"
fi

# missing param, exit
if [ -z "$1" ]; then
    echo "need 1 param for deploy.id"
    exit 1
fi

# if proc exists, exit
TARGET_SCRIPT="run_gpu_monitor_otlp.py"
if ps -ef | grep "$TARGET_SCRIPT" | grep -v grep > /dev/null; then
    echo "Monitor process '$TARGET_SCRIPT' is already running. Exiting."
    exit 0
fi

# install dependencies
export PIP_INDEX_URL="https://mirrors.aliyun.com/pypi/simple/"
python3 -m pip install psutil nvidia-ml-py openlit

# run monitor
python3 "$SCRIPT_DIR/run_gpu_monitor_otlp.py" -u http://otel-agent.em:32317 -n $1

# run monitor (background)
# nohup python3 "$SCRIPT_DIR/run_gpu_monitor_otlp.py" -u http://otel-agent.em:32317 -n $1 > /proc/1/fd/1 2>&1 < /dev/null &