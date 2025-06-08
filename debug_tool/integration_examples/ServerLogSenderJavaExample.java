// ServerLogSenderJavaExample.java
package com.example.debugui.integration;

import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.logging.Handler;
import java.util.logging.LogRecord;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter; // Or any other formatter

/**
 * Conceptual example of a java.util.logging Handler for sending logs over TCP.
 * This would need to be adapted for Log4j, Logback, or other logging frameworks
 * if they are used in xiaozhi-esp32-server's Java components.
 */
class TCPSocketHandler extends Handler {
    private Socket socket;
    private PrintWriter writer;
    private String host;
    private int port;
    private String sourceId; // e.g., "JAVA_SERVER_MODULE_X"

    public TCPSocketHandler(String host, int port, String sourceId) throws IOException {
        this.host = host;
        this.port = port;
        this.sourceId = sourceId;
        connect();
        // Using a SimpleFormatter or a custom one
        setFormatter(new SimpleFormatter());
    }

    private void connect() throws IOException {
        try {
            this.socket = new Socket(host, port);
            this.writer = new PrintWriter(socket.getOutputStream(), true); // autoFlush=true
            System.out.println(sourceId + ": Successfully connected to Debug UI at " + host + ":" + port);
             // Optional: Send a connection confirmation
            // this.writer.println(sourceId + "_LOG_STREAM_CONNECTED");
        } catch (UnknownHostException e) {
            System.err.println(sourceId + ": Unknown host " + host + ". " + e.getMessage());
            throw e; // Propagate to prevent handler from being used if connection fails initially
        } catch (IOException e) {
            System.err.println(sourceId + ": Could not connect to " + host + ":" + port + ". " + e.getMessage());
            throw e;
        }
    }

    @Override
    public void publish(LogRecord record) {
        if (!isLoggable(record) || writer == null) {
            return;
        }
        String message;
        try {
            message = getFormatter().format(record); // Format the log record
        } catch (Exception e) {
            reportError("Error formatting log record", e, java.util.logging.ErrorManager.FORMAT_FAILURE);
            return;
        }

        try {
            // Prepend sourceId if needed, though backend already adds [SERVER]
            // writer.println("[" + sourceId + "] " + message.trim());
            writer.println(message.trim()); // Send trimmed message
            if (writer.checkError()) { // Check for errors after println
                throw new IOException("PrintWriter encountered an error.");
            }
        } catch (Exception e) {
            // Handle disconnections and attempt to reconnect
            reportError("Error writing log record to socket, attempting reconnect.", e, java.util.logging.ErrorManager.WRITE_FAILURE);
            try {
                if (socket != null) socket.close();
            } catch (IOException ex) {
                // Ignore
            }
            try {
                connect(); // Attempt to reconnect
                // Retry sending the message (optional, be careful with loops)
                writer.println(message.trim());
            } catch (IOException ex) {
                reportError("Failed to reconnect or resend log.", ex, java.util.logging.ErrorManager.WRITE_FAILURE);
            }
        }
    }

    @Override
    public void flush() {
        if (writer != null) {
            try {
                writer.flush();
            } catch (Exception e) {
                reportError("Error flushing writer.", e, java.util.logging.ErrorManager.FLUSH_FAILURE);
            }
        }
    }

    @Override
    public void close() throws SecurityException {
        if (writer != null) {
            try {
                writer.flush();
                writer.close();
            } catch (Exception e) {
                 reportError("Error closing writer.", e, java.util.logging.ErrorManager.CLOSE_FAILURE);
            }
        }
        if (socket != null) {
            try {
                socket.close();
            } catch (IOException e) {
                 reportError("Error closing socket.", e, java.util.logging.ErrorManager.CLOSE_FAILURE);
            }
        }
        writer = null;
        socket = null;
    }
}

public class ServerLogSenderJavaExample {
    private static final Logger logger = Logger.getLogger(ServerLogSenderJavaExample.class.getName());
    private static final String DEBUG_UI_HOST = "localhost";
    private static final int DEBUG_UI_PORT = 6002; // Port for SERVER logs

    public static void main(String[] args) {
        System.out.println("Starting xiaozhi-esp32-server JAVA log sender demonstration...");
        System.out.println("Attempting to send logs to Debug UI at " + DEBUG_UI_HOST + ":" + DEBUG_UI_PORT);

        try {
            // Remove default console handlers if you only want TCP logs for this demo
            // Logger rootLogger = Logger.getLogger("");
            // Handler[] handlers = rootLogger.getHandlers();
            // if (handlers[0] instanceof java.util.logging.ConsoleHandler) {
            //     rootLogger.removeHandler(handlers[0]);
            // }

            TCPSocketHandler tcpHandler = new TCPSocketHandler(DEBUG_UI_HOST, DEBUG_UI_PORT, "JAVA_MAIN_APP");
            logger.addHandler(tcpHandler);
            logger.setLevel(java.util.logging.Level.INFO); // Set desired log level

            logger.info("Java component of xiaozhi-esp32-server starting...");
            Thread.sleep(500);
            logger.info("Initializing database connection pool...");
            Thread.sleep(500);
            logger.warning("External API 'AuthService' response time is high.");
            Thread.sleep(500);
            logger.severe("Failed to load configuration module 'module-iot-plugins'.");
            Thread.sleep(500);
            logger.info("Java component shutting down simulation.");

        } catch (IOException e) {
            System.err.println("Could not start TCP log handler: " + e.getMessage());
            e.printStackTrace();
        } catch (InterruptedException e) {
            System.err.println("Demo interrupted: " + e.getMessage());
        } finally {
             System.out.println("Closing Java log handlers if any were TCPSocketHandlers (manual close needed for demo).");
             // In a real app, lifecycle management of handlers is important.
             // For this demo, direct handler close is not straightforward without storing it.
             // logger.getHandlers()[0].close(); // if you are sure about the handler
        }
        System.out.println("Java log demonstration finished.");
    }
}
