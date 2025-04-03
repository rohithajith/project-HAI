from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
import os
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

class AgentLogHandler(FileSystemEventHandler):
    """Watch the agent_logs directory for new log files and emit updates."""
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.json'):
            try:
                with open(event.src_path, 'r') as log_file:
                    log_data = json.load(log_file)
                
                # Extract relevant update information
                frontend_update = log_data.get('frontend_update', {})
                if frontend_update:
                    # Emit the update to connected clients
                    socketio.emit('agent_update', {
                        'component': frontend_update.get('component', 'default'),
                        'action': frontend_update.get('action', 'update'),
                        'message': frontend_update.get('message', ''),
                        'details': log_data
                    })
            except Exception as e:
                print(f"Error processing log file {event.src_path}: {e}")

def start_log_watcher():
    """Start watching the agent_logs directory for new log files."""
    logs_dir = os.path.join(os.getcwd(), 'agent_logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    event_handler = AgentLogHandler()
    observer = Observer()
    observer.schedule(event_handler, logs_dir, recursive=False)
    observer.start()
    
    return observer

@app.route('/')
def index():
    """Simple route to show WebSocket is working."""
    return "Agent Update WebSocket Server is running"

@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket client connections."""
    print('Client connected')
    emit('connection_response', {'message': 'Connected to Agent Update Server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnections."""
    print('Client disconnected')

def run_websocket_server():
    """Run the WebSocket server."""
    log_observer = start_log_watcher()
    try:
        socketio.run(app, host='0.0.0.0', port=5001, debug=True)
    finally:
        log_observer.stop()
        log_observer.join()

if __name__ == '__main__':
    run_websocket_server()