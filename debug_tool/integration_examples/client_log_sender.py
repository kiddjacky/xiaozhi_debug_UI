import logging
import socket
import time
import sys

# Configuration for the Debug UI Backend TCP listener for CLIENT logs
DEBUG_UI_HOST = 'localhost'
DEBUG_UI_PORT = 6001 # Port for client logs

class TCPSocketHandler(logging.Handler):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = None
        self.retry_interval = 5 # seconds
        self.connect()

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            # Send a connection confirmation message (optional)
            # self.socket.sendall(b"CLIENT_LOG_STREAM_CONNECTED\n")
            print(f"Successfully connected to Debug UI at {self.host}:{self.port}")
        except socket.error as e:
            print(f"Failed to connect to Debug UI at {self.host}:{self.port}. Error: {e}. Retrying in {self.retry_interval}s...", file=sys.stderr)
            self.socket = None # Ensure socket is None if connection failed
            # Schedule a retry without blocking everything if this were in a more complex app
            # For this demo, we might just error out or let emit handle retries.

    def emit(self, record):
        if self.socket is None:
            # Attempt to reconnect if socket is not available
            print("Socket not connected. Attempting to reconnect...", file=sys.stderr)
            self.connect()
            if self.socket is None: # Still not connected
                print("Reconnect failed. Log message will be lost.", file=sys.stderr)
                return

        try:
            msg = self.format(record) + "\n" # Ensure newline for readline on server
            self.socket.sendall(msg.encode('utf-8'))
        except socket.error as e:
            print(f"Socket error while sending log: {e}. Attempting to reconnect...", file=sys.stderr)
            self.socket.close() # Close the broken socket
            self.socket = None
            self.connect() # Try to immediately reconnect
            if self.socket: # If reconnected, try sending again (optional, could lead to loops)
                try:
                    self.socket.sendall(msg.encode('utf-8'))
                except Exception as e_retry:
                     print(f"Failed to send log even after reconnect: {e_retry}", file=sys.stderr)
            else:
                print("Log message lost due to send failure after reconnect attempt.", file=sys.stderr)
        except Exception as e:
            # Catch any other exceptions during emit
            print(f"General error during log emit: {e}", file=sys.stderr)
            # We might want to close and attempt reconnect here too
            if self.socket:
                self.socket.close()
            self.socket = None


    def close(self):
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                print(f"Error closing socket: {e}", file=sys.stderr)
        super().close()

def setup_py_xiaozhi_logging():
    '''
    This function demonstrates how py-xiaozhi's logging could be configured.
    In the actual py-xiaozhi client, this setup would be integrated
    into its existing logging configuration.
    '''
    logger = logging.getLogger('py_xiaozhi_client_example') # Use a specific logger name
    logger.setLevel(logging.INFO)

    # Standard console handler (optional, py-xiaozhi likely has this)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    # Custom TCP handler for Debug UI
    tcp_handler = TCPSocketHandler(host=DEBUG_UI_HOST, port=DEBUG_UI_PORT)
    tcp_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')) # Format for logs sent to Debug UI
    logger.addHandler(tcp_handler)

    return logger

if __name__ == "__main__":
    # This is a demonstration of how the logger would be used.
    # In py-xiaozhi, you would get the logger configured in its main application.

    print("Starting py-xiaozhi client log sender demonstration...")
    print(f"Attempting to send logs to Debug UI at {DEBUG_UI_HOST}:{DEBUG_UI_PORT}")

    # Get the logger instance (as if it's from py-xiaozhi)
    # In a real integration, you'd find where py-xiaozhi configures its logging
    # and add the TCPSocketHandler there.
    client_logger = setup_py_xiaozhi_logging()

    # Simulate some log messages from py-xiaozhi
    try:
        client_logger.info("py-xiaozhi client starting up...")
        time.sleep(1)
        client_logger.info("Initializing components...")
        time.sleep(1)
        client_logger.warning("A minor issue occurred, but it's handled.")
        time.sleep(1)
        client_logger.info("User 'test_user' attempting to connect.")
        time.sleep(1)
        client_logger.error("Failed to connect to external service XYZ.")
        time.sleep(1)
        client_logger.info("Shutting down py-xiaozhi client simulation.")
    except KeyboardInterrupt:
        print("Demonstration stopped by user.")
    except Exception as e:
        client_logger.error(f"An unexpected error occurred in demo: {e}", exc_info=True)
    finally:
        print("Closing log handlers...")
        # Important: Close handlers to ensure sockets are closed properly
        for handler in client_logger.handlers:
            if isinstance(handler, TCPSocketHandler): # Close custom handler
                handler.close()
            # For other handlers, logging.shutdown() might be used in a full app
        logging.shutdown() # Flushes and closes all handlers

        print("Demonstration finished.")
