# Required Dependencies:
# pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp

import argparse
import time
import sys
import platform
import socket

try:
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk._logs import LoggerProvider, LogRecord
    from opentelemetry.sdk._logs.export import SimpleLogRecordProcessor
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
    from opentelemetry._logs import SeverityNumber
except ImportError:
    print("[-] Missing required dependencies.")
    print(
        "    Please run: pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp"
    )
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Send a test log to an OTLP endpoint using OpenTelemetry SDK (gRPC)."
    )
    parser.add_argument(
        "-u",
        "--url",
        required=True,
        help="Target OTLP endpoint URL (e.g., http://127.0.0.1:4317)",
    )
    parser.add_argument("-n", "--name", default="test-service", help="Service name")
    args = parser.parse_args()

    print(f"[*] Target Endpoint: {args.url}")
    print(f"[*] Service Name: {args.name}")

    provider = None
    try:
        # Configure OTLP gRPC Exporter
        exporter = OTLPLogExporter(endpoint=args.url, insecure=True)

        # Get system information
        full_os_info = f"{socket.gethostname()} | {platform.system()} {platform.release()} {platform.version()} | {platform.machine()} | {platform.processor()}"

        resource = Resource.create(
            {
                "service.name": args.name,
                "os.info": full_os_info,
            }
        )
        provider = LoggerProvider(resource=resource)

        # Use SimpleLogRecordProcessor for immediate export
        provider.add_log_record_processor(SimpleLogRecordProcessor(exporter))

        # Get a logger from the provider (NOT the standard python logging module)
        logger = provider.get_logger("otlp-tester")

        print("[*] Sending log...")
        timestamp = int(time.time() * 1e9)

        # Emit a log record directly
        logger.emit(
            LogRecord(
                timestamp=timestamp,
                observed_timestamp=timestamp,
                severity_number=SeverityNumber.INFO,
                severity_text="INFO",
                body="test_otlp",
                resource=resource,
            )
        )

        # Force flush to ensure it's sent
        provider.force_flush()
        print("[+] Log sent successfully!")

    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)
    finally:
        # CRITICAL: Explicitly shutdown the provider to clean up resources/threads
        # This prevents "RuntimeError: can't create new thread at interpreter shutdown"
        if provider:
            provider.shutdown()


if __name__ == "__main__":
    main()
