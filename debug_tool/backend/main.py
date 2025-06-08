import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

# Configure basic logging for the backend itself
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- WebSocket Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New frontend connection: {websocket.client}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Frontend connection closed: {websocket.client}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection.client}: {e}")
                # Optionally remove problematic connections here
                # self.active_connections.remove(connection) # Be careful with modifying list while iterating

manager = ConnectionManager()
log_queue = asyncio.Queue()

# --- TCP Log Receivers ---
async def handle_log_stream(reader, writer, source_name: str):
    addr = writer.get_extra_info('peername')
    logger.info(f"Accepted {source_name} log connection from {addr}")
    try:
        while True:
            data = await reader.readline()
            if not data:
                logger.info(f"{source_name} log connection {addr} closed by peer.")
                break
            message = data.decode().strip()
            # Add source name prefix for frontend to distinguish
            await log_queue.put(f"[{source_name.upper()}] {message}")
    except ConnectionResetError:
        logger.warning(f"{source_name} log connection {addr} reset.")
    except asyncio.IncompleteReadError:
        logger.warning(f"{source_name} log connection {addr} closed with incomplete read.")
    except Exception as e:
        logger.error(f"Error in {source_name} log stream from {addr}: {e}")
    finally:
        logger.info(f"Closing {source_name} log connection from {addr}")
        try:
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            logger.error(f"Error closing writer for {addr}: {e}")


async def start_tcp_server(host: str, port: int, source_name: str):
    server = await asyncio.start_server(
        lambda r, w: handle_log_stream(r, w, source_name),
        host, port)
    logger.info(f"{source_name} log receiver listening on {host}:{port}")
    async with server:
        await server.serve_forever()

# --- Log Broadcaster Task ---
async def broadcast_logs():
    logger.info("Log broadcaster task started.")
    while True:
        log_message = await log_queue.get()
        await manager.broadcast(log_message)
        log_queue.task_done()

# --- FastAPI Endpoints ---
@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # This keeps the connection alive. Client messages could be processed here if needed.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error for {websocket.client}: {e}")
        manager.disconnect(websocket)

# --- Static Files Setup ---
# Determine the path to the frontend directory
# Assumes main.py is in debug_tool/backend/ and frontend is in debug_tool/frontend/
current_file_path = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(current_file_path, "..", "frontend")

# Mount the 'frontend' directory to serve static files (HTML, CSS, JS)
# html=True allows serving 'index.html' for directory root requests (e.g., GET /)
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend_static")

# --- Application Startup ---
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Debug UI Backend Service...")
    # Start TCP servers for client and server logs
    # These will run in the background
    asyncio.create_task(start_tcp_server("0.0.0.0", 6001, "client"))
    asyncio.create_task(start_tcp_server("0.0.0.0", 6002, "server"))
    # Start the log broadcaster task
    asyncio.create_task(broadcast_logs())
    logger.info("Debug UI Backend Service tasks scheduled.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
