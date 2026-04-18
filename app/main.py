from flask import Flask, jsonify, request
from markupsafe import escape
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for container orchestration probes."""
    return jsonify({"status": "healthy"}), 200

@app.route('/hello', methods=['GET'])
def hello():
    """A simple greeting endpoint demonstrating input sanitization."""
    name = request.args.get('name', 'World')
    # Sanitize input to prevent injection attacks
    safe_name = escape(name)
    return jsonify({"message": f"Hello, {safe_name}!"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
