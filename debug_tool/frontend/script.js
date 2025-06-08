document.addEventListener('DOMContentLoaded', () => {
    const logContainer = document.getElementById('logContainer');
    const clearLogsBtn = document.getElementById('clearLogsBtn');
    const filterInput = document.getElementById('filterInput');
    let websocket;

    function connectWebSocket() {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/logs`;
        websocket = new WebSocket(wsUrl);

        websocket.onopen = () => {
            console.log('WebSocket connection established');
            addLogMessage('System: Connected to log server.', 'system');
        };

        websocket.onmessage = (event) => {
            const message = event.data;
            addLogMessage(message); // Type will be inferred from prefix in addLogMessage
        };

        websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            addLogMessage('System: WebSocket error. Check console.', 'error system');
        };

        websocket.onclose = () => {
            console.log('WebSocket connection closed. Attempting to reconnect...');
            addLogMessage('System: Disconnected. Attempting to reconnect in 3s...', 'system error');
            setTimeout(connectWebSocket, 3000);
        };
    }

    function addLogMessage(message, baseClasses = '') {
        const filterText = filterInput.value.toLowerCase();
        if (filterText && !message.toLowerCase().includes(filterText)) {
            return;
        }

        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry'; // Base class
        if(baseClasses) { // Add any explicit classes like 'system' or 'error'
             baseClasses.split(' ').forEach(cls => {
                if(cls) logEntry.classList.add(cls);
            });
        }

        // Add styling based on message content
        if (message.startsWith('[CLIENT]')) {
            logEntry.classList.add('client');
        } else if (message.startsWith('[SERVER]')) {
            logEntry.classList.add('server');
        } else if (message.toLowerCase().includes('error')) {
            logEntry.classList.add('error');
        } else if (message.toLowerCase().includes('warning')) {
            logEntry.classList.add('warning');
        }

        logEntry.textContent = message; // Use textContent to prevent XSS
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    clearLogsBtn.addEventListener('click', () => {
        logContainer.innerHTML = '';
        addLogMessage('System: Logs cleared.', 'system');
    });

    filterInput.addEventListener('input', () => {
        // This is a simple filter that applies to new messages.
        // For a live filter of existing messages, one would need to iterate over
        // existing log entries and toggle their display.
        // For now, we just log that the filter value changed.
        console.log(`Filter input changed to: ${filterInput.value}`);
    });

    connectWebSocket();
});
