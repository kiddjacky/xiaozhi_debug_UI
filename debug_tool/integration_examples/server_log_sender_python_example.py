import logging
import socket
import time
import sys

DEBUG_UI_HOST = 'localhost'
DEBUG_UI_PORT = 6002 # Port for SERVER logs

class TCPSocketHandler(logging.Handler):
    def __init__(self, host, port, source_id="PYTHON_SERVER"): # Added source_id
        super().__init__()
        self.host = host
        self.port = port
        self.source_id = source_id # To help identify log source if server has multiple components
        self.socket = None
        self.retry_interval = 5 # seconds
        self.connect()

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Successfully connected {self.source_id} log sender to Debug UI at {self.host}:{self.port}")
        except socket.error as e:
            print(f"Failed to connect {self.source_id} to Debug UI at {self.host}:{self.port}. Error: {e}. Retrying in {self.retry_interval}s...", file=sys.stderr)
            self.socket = None

    def emit(self, record):
        if self.socket is None:
            print(f"{self.source_id}: Socket not connected. Attempting to reconnect...", file=sys.stderr)
            self.connect()
            if self.socket is None:
                print(f"{self.source_id}: Reconnect failed. Log message will be lost.", file=sys.stderr)
                return
        try:
            # The backend already prefixes with [SERVER], so no need for source_id in basic message here
            # unless more granularity is desired.
            msg = self.format(record) + "\n"
            self.socket.sendall(msg.encode('utf-8'))
        except socket.error as e:
            print(f"{self.source_id}: Socket error while sending log: {e}. Attempting to reconnect...", file=sys.stderr)
            if self.socket:
                self.socket.close()
            self.socket = None
            self.connect()
            if self.socket:
                try:
                    self.socket.sendall(msg.encode('utf-8'))
                except Exception as e_retry:
                    print(f"{self.source_id}: Failed to send log even after reconnect: {e_retry}", file=sys.stderr)
            else:
                print(f"{self.source_id}: Log message lost due to send failure after reconnect attempt.", file=sys.stderr)
        except Exception as e:
            print(f"{self.source_id}: General error during log emit: {e}", file=sys.stderr)
            if self.socket:
                self.socket.close()
            self.socket = None

    def close(self):
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                print(f"{self.source_id}: Error closing socket: {e}", file=sys.stderr)
        super().close()

def setup_server_python_logging():
    logger = logging.getLogger('xiaozhi_server_python_example')
    logger.setLevel(logging.DEBUG) # Server might log more verbosely

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    tcp_handler = TCPSocketHandler(host=DEBUG_UI_HOST, port=DEBUG_UI_PORT, source_id="SERVER_PYTHON_MAIN")
    tcp_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - [%(module)s.%(funcName)s:%(lineno)d] - %(message)s'))
    logger.addHandler(tcp_handler)

    return logger

if __name__ == "__main__":
    print("Starting xiaozhi-esp32-server PYTHON log sender demonstration...")
    print(f"Attempting to send logs to Debug UI at {DEBUG_UI_HOST}:{DEBUG_UI_PORT}")

    server_logger = setup_server_python_logging()

    try:
        server_logger.info("Python component of xiaozhi-esp32-server starting...")
        time.sleep(0.5)
        server_logger.debug("Handling incoming API request /api/v1/status")
        time.sleep(0.5)
        server_logger.info("Processing data for user 'device_001'")
        time.sleep(0.5)
        server_logger.warning("Database connection pool nearing capacity.")
        time.sleep(0.5)
        try:
            # Simulate an error
            x = 1 / 0
        except Exception as e:
            server_logger.error(f"Critical error processing request: {e}", exc_info=True) # exc_info=True includes stack trace
        time.sleep(0.5)
        server_logger.info("Python component shutting down simulation.")
    except KeyboardInterrupt:
        print("Server Python log demonstration stopped by user.")
    except Exception as e:
        server_logger.critical(f"An unexpected critical error occurred in demo: {e}", exc_info=True)
    finally:
        print("Closing server Python log handlers...")
        for handler in server_logger.handlers:
            if isinstance(handler, TCPSocketHandler):
                handler.close()
        logging.shutdown()
        print("Server Python log demonstration finished.")
