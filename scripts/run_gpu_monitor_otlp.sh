#!/bin/bash
if [ -z "$1" ]; then
    echo "missing param to distinguish this deploy, e.g., 'qwen3-4b_h20'"
    exit 1
fi
DEPLOY_NAME="$1"

REMOTE_HOST_URL=${REMOTE_HOST_URL:-"https://dd-ai-service.eastmoney.com/aip-files/f"}
OTLP_URL=${OTLP_URL:-"http://otel-agent.em:32317"}

# if proc exists, exit
PYTHON_SCRIPT="run_gpu_monitor_otlp.py"
if ps -ef | grep "$PYTHON_SCRIPT" | grep -v grep > /dev/null; then
    echo "Monitor process '$PYTHON_SCRIPT' is already running. Exiting."
    exit 0
fi

# install dependencies
export PIP_INDEX_URL="https://mirrors.aliyun.com/pypi/simple/"
PIP_DEPS=(psutil nvidia-ml-py openlit)
if command -v uv >/dev/null 2>&1; then
    echo "uv found, run 'uv pip install'..."
    uv pip install "${PIP_DEPS[@]}"
else
    echo "run 'python3 -m pip install'..."
    if ! python3 -m pip install "${PIP_DEPS[@]}"; then
        echo "run 'pip install'..."
        pip install "${PIP_DEPS[@]}"
    fi
fi

# download python script
echo "Downloading $PYTHON_SCRIPT..."
curl -fsSL "$REMOTE_HOST_URL/sh/$PYTHON_SCRIPT" -o "$PYTHON_SCRIPT"

# run
echo "Running monitor: OTLP_URL=$OTLP_URL, DEPLOY_NAME=$DEPLOY_NAME"
nohup python3 "$PYTHON_SCRIPT" -u $OTLP_URL -n $DEPLOY_NAME > /proc/1/fd/1 2>&1 < /dev/null &


# curl -fsSL "https://dd-ai-service.eastmoney.com/aip-files/f/sh/run_gpu_monitor_otlp.sh" | tr -d '\r' | bash -s -- "qwen3-4b_h20"