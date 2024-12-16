from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Simulated storage for user logs (use a database in production)
user_logs = []

@app.route('/log', methods=['POST'])
def log_action():
    # Extract data from the POST request
    data = request.json
    action = data.get("action")
    model = data.get("model")

    if not action or not model:
        return jsonify({"error": "Action and model are required"}), 400

    # Log entry with timestamp
    log_entry = {
        "user" : 1,
        "action": action,
        "model": model,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Append to log storage
    user_logs.append(log_entry)
    return jsonify({"message": "Log recorded successfully", "log": log_entry}), 200

@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify(user_logs), 200

if __name__ == "__main__":
    app.run(debug=True)
