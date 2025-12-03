# Required Dependencies:
# pip install psutil nvidia-ml-py openlit

# Example usage:
# python scripts/run_gpu_monitor_otlp.py -u http://127.0.0.1:4317 -n volce_qwen3-4b

import platform
import signal
import os
import argparse
import socket
from threading import Event


keep_running = Event()


def signal_handler(sig, frame):
    global keep_running
    print(f"recv_terminate_signal: signal={sig}")
    keep_running.set()


def main():
    parser = argparse.ArgumentParser(
        description="Continuously monitor gpu metrics and send them to an OTLP endpoint."
    )
    parser.add_argument(
        "-u",
        "--url",
        required=True,
        help="Target OTLP endpoint URL (e.g., http://127.0.0.1:4317)",
    )
    parser.add_argument("-s", "--service", default="gpu-monitor", help="Service name")
    parser.add_argument("-n", "--name", required=True, help="Distinct deployment name")
    parser.add_argument(
        "--http", action="store_true", help="Use HTTP protocol for OTLP"
    )
    args = parser.parse_args()

    if not args.http:
        os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "grpc"
        print("enable_grpc")

    # Add deploy.id to OTEL_RESOURCE_ATTRIBUTES
    current_attrs = os.environ.get("OTEL_RESOURCE_ATTRIBUTES", "")

    hostname = socket.gethostname()
    # ensure deploy.id is unique per machine
    deploy_id = f"{args.name}_{hostname}"
    new_attr = f"deploy.id={deploy_id},machine.hostname={hostname},machine.system={platform.system()},machine.release={platform.release()},machine.version={platform.version()},machine.architecture={platform.machine()}"

    if current_attrs:
        os.environ["OTEL_RESOURCE_ATTRIBUTES"] = f"{current_attrs},{new_attr}"
    else:
        os.environ["OTEL_RESOURCE_ATTRIBUTES"] = new_attr
    print(f"set_attributes: attributes={os.environ['OTEL_RESOURCE_ATTRIBUTES']}")

    try:
        import openlit

        openlit.init(
            service_name=args.service,
            application_name=args.name,
            otlp_endpoint=args.url,
            collect_gpu_stats=True,
        )

        print("register_signal: signals=[SIGTERM,SIGINT]")
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        print("keep_running")
        global keep_running
        while not keep_running.is_set():
            # for Windows, wait time must be set
            keep_running.wait(1)
    except Exception as e:
        print(f"err_occurred: {e}")
    finally:
        print("exited")


if __name__ == "__main__":
    main()
