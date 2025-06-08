# Real-time Debug UI for py-xiaozhi and xiaozhi-esp32-server

This tool provides a web-based interface to view real-time aggregated logs from both the `py-xiaozhi` client and the `xiaozhi-esp32-server`. It helps developers and testers monitor the behavior and diagnose issues across these distributed components in a unified view.

## Features

-   **Real-time Log Streaming:** Logs from client and server are displayed as they occur.
-   **Consolidated View:** Client and server logs are shown in a single interface, tagged for easy identification.
-   **Simple Filtering:** Filter logs by keywords.
-   **Log Clearing:** Clear the displayed logs from the UI.
-   **TCP-based Log Ingestion:** Client and server applications send logs over simple TCP connections.
-   **Web-based UI:** Accessible from any modern web browser.

## Architecture

The Debug UI tool consists of three main parts:

1.  **Debug UI Backend (`debug_tool/backend/`):**
    - A Python FastAPI application.
    - Listens for TCP connections from `py-xiaozhi` on port `6001` for client logs.
    - Listens for TCP connections from `xiaozhi-esp32-server` on port `6002` for server logs.
    - Serves the static frontend files (HTML, CSS, JS).
    - Provides a WebSocket endpoint (`/ws/logs`) that the frontend connects to for receiving aggregated logs.
    - Runs on `http://localhost:8000` by default.

2.  **Debug UI Frontend (`debug_tool/frontend/`):**
    - A single-page web application (HTML, CSS, JavaScript).
    - Connects to the backend's WebSocket.
    - Displays logs, allows filtering and clearing.

3.  **Log Sender Integration Examples (`debug_tool/integration_examples/`):**
    - Example scripts and code snippets showing how to modify `py-xiaozhi` (Python) and `xiaozhi-esp32-server` (Python, Java) to send their logs to the Debug UI Backend.

## Setup and Running the Debug UI

1.  **Prerequisites:**
    - Python 3.7+
    - `pip` (Python package installer)

2.  **Get the Tool:**
    - If this tool is part of a larger repository, navigate to the `debug_tool` directory.
    - If distributed separately, clone or download the `debug_tool` directory.

3.  **Install Dependencies:**
    Open a terminal in the `debug_tool/backend/` directory and run:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Debug UI Backend:**
    While still in the `debug_tool/backend/` directory, run:
    ```bash
    python main.py
    ```
    You should see output indicating the server has started, including lines like:
    ```
    INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
    INFO:     client log receiver listening on 0.0.0.0:6001
    INFO:     server log receiver listening on 0.0.0.0:6002
    ```

5.  **Access the Frontend:**
    Open your web browser and navigate to:
    [http://localhost:8000](http://localhost:8000)

## Integrating Your Applications (Log Senders)

To see logs from `py-xiaozhi` and `xiaozhi-esp32-server` in this Debug UI, you need to configure them to send their logs to the Debug UI Backend.

-   **Detailed instructions and example code are provided in:**
    [`debug_tool/integration_examples/README.md`](./integration_examples/README.md)

-   **Quick Summary:**
    -   `py-xiaozhi` (client) should send its logs via TCP to port `6001` of the machine running the Debug UI Backend.
    -   `xiaozhi-esp32-server` components should send their logs via TCP to port `6002`.

## How to Use the Debug UI

1.  **Start the Debug UI Backend** as described in the setup instructions.
2.  **Modify and Start `py-xiaozhi`:** Integrate the TCP logging handler (see integration examples) into your `py-xiaozhi` client and start it.
3.  **Modify and Start `xiaozhi-esp32-server`:** Integrate the TCP logging handler(s) into your `xiaozhi-esp32-server` components (Python/Java) and start them.
4.  **Open the Debug UI Frontend** in your browser (`http://localhost:8000`).
5.  Logs from both applications should start appearing in the web interface, prefixed with `[CLIENT]` or `[SERVER]`.
6.  Use the "Filter" input to show only logs containing specific keywords.
7.  Use the "Clear Logs" button to clear the current display.

## Troubleshooting

-   **No logs appearing in the UI:**
    -   Ensure the Debug UI Backend (`main.py`) is running and you see no errors in its console.
    -   Verify that your `py-xiaozhi` client and/or `xiaozhi-esp32-server` are running and have been correctly modified to send logs to the configured host/ports (`localhost:6001` for client, `localhost:6002` for server, by default).
    -   Check the console output of your client/server applications for any errors related to logging or connecting to the Debug UI TCP ports.
    -   Ensure there are no firewall rules blocking TCP connections to ports 6001, 6002, or 8000 on the machine running the Debug UI backend.
-   **"System: WebSocket error" or "System: Disconnected" in the UI:**
    -   This indicates an issue with the WebSocket connection between your browser and the Debug UI Backend.
    -   Check the Debug UI Backend's console output for any errors.
    -   Ensure your network connection is stable.
    -   Try refreshing the browser page.
