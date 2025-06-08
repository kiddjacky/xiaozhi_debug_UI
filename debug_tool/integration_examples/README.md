# Integration Examples for Debug UI

This directory contains example scripts demonstrating how to integrate client and server applications with the Debug UI logging system.

## `client_log_sender.py`

This script shows how a Python application (like `py-xiaozhi`) can be configured to send its logs to the Debug UI backend.

**How it works:**
- It defines a custom `TCPSocketHandler` for Python's `logging` module.
- This handler connects to the Debug UI backend's TCP server (typically `localhost:6001` for client logs).
- Log messages are formatted and sent over this TCP connection.

**To use this as a reference for `py-xiaozhi`:**
1.  Copy or adapt the `TCPSocketHandler` class into the `py-xiaozhi` codebase.
2.  In `py-xiaozhi`'s logging configuration (wherever `logging.getLogger()` or `logging.basicConfig()` is used), add an instance of this `TCPSocketHandler` to the appropriate logger(s).
3.  Ensure the `host` and `port` for the handler are correctly set to where the Debug UI backend is running.

You can run this script directly (`python client_log_sender.py`) while the Debug UI backend is active to see example client logs appear in the Debug UI frontend.

## `server_log_sender_python_example.py`

This script demonstrates how Python components within `xiaozhi-esp32-server` can send logs to the Debug UI backend.

**How it works:**
- Similar to `client_log_sender.py`, it uses a `TCPSocketHandler`.
- It's configured to send logs to the Debug UI backend's TCP server for server logs (typically `localhost:6002`).
- Includes a `source_id` in the handler for potential differentiation if multiple Python components in the server send logs.

**To use this as a reference for `xiaozhi-esp32-server` (Python parts):**
1.  Adapt the `TCPSocketHandler` into the server's Python codebase.
2.  Integrate this handler into the logging configuration of relevant Python modules/services within the server.
3.  Ensure correct `host`, `port`, and `source_id`.

Run with `python server_log_sender_python_example.py` while the Debug UI is active.

## `ServerLogSenderJavaExample.java`

This file provides a conceptual example of how Java components within `xiaozhi-esp32-server` could send logs using a custom `java.util.logging.Handler`.

**How it works (Conceptual):**
- Defines a `TCPSocketHandler` that extends `java.util.logging.Handler`.
- This handler would connect to the Debug UI backend (e.g., `localhost:6002`).
- Formatted log records would be sent over the TCP connection.

**To use this as a reference for `xiaozhi-esp32-server` (Java parts):**
1.  This code would need to be compiled and integrated into the server's Java components.
2.  If a different logging framework (like Log4j or Logback) is used, a similar custom appender/handler would need to be written for that specific framework.
3.  The core logic involves opening a socket, formatting the log message, and sending it. Error handling and reconnection logic are important.

This Java example is for illustration and would require adaptation to the server's specific Java environment and logging framework.
