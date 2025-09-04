#!/usr/bin/env python3

"""
Emergency Rating Calculator - Main Flask Application
IEC 60853-2 Compliant Underground Cable Thermal Analysis
"""

import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

# Import thermal routes
from routes.thermal import thermal_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
socketio = SocketIO(app)

#app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'emergency_rating_calculator_secret_key'

# Enable CORS for all routes
CORS(app)

# Register thermal calculation blueprint
app.register_blueprint(thermal_bp, url_prefix='/api/thermal')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve static files"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    
if __name__ == '__main__':
    print("Starting Emergency Rating Calculator...")
    print("Available at: http://localhost:5000")
    print("API endpoints at: http://localhost:5000/api/thermal/")

    socketio.run(app, debug=False, port=5000, allow_unsafe_werkzeug=True) # Starts the server
    #app.run(host='0.0.0.0', port=5555, debug=True)

