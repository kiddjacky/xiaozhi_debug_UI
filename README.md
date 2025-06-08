# Xiaozhi Debug UI

This project provides a simple web-based UI to send requests to a Python backend client for debugging purposes.

## Project Structure

-   `debug_ui/`: Contains the HTML and JavaScript for the frontend debug interface.
    -   `index.html`: The main page for the debug UI.
-   `py_xiaozhi_client/`: Contains the Python backend client.
    -   `client.py`: A Flask-based web server that listens for requests from the debug UI.

## Setup and Installation

1.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2.  **Install Python dependencies:**
    The backend client uses Flask. Install it using pip:
    ```bash
    pip install Flask
    ```

## Running the Application

1.  **Run the Python client:**
    Navigate to the project's root directory in your terminal and run:
    ```bash
    python py_xiaozhi_client/client.py
    ```
    This will start the Flask development server, typically on `http://localhost:5000`. You should see output indicating the server is running.

2.  **Open the Debug UI:**
    Open the `debug_ui/index.html` file in your web browser.

## How it Works

The Debug UI (`index.html`) provides a simple form to send data. When you submit the form:
1.  JavaScript in the `index.html` page captures the input data.
2.  It sends a POST request with the data in JSON format to the `/debug_request` endpoint of the Python client (`http://localhost:5000/debug_request`).
3.  The Python client (`client.py`) receives the request, prints the received data to its console, and sends back a JSON response.
4.  The Debug UI displays a status message based on the server's response.

## Example Usage

1.  Ensure the Python client is running (as described in "Running the Application").
2.  Open `debug_ui/index.html` in your browser.
3.  In the "Request Data:" input field, type any message you want to send (e.g., "Hello Xiaozhi").
4.  Click the "Send Request" button.
5.  **Check the Python client console:** You should see the message printed, for example:
    ```
    Received request: {'data': 'Hello Xiaozhi'}
    ```
6.  **Check the Debug UI:** The UI will display a message like:
    `Server response: Request received`

    The underlying JSON response received by the UI from the server is:
    ```json
    {"status": "success", "message": "Request received"}
    ```