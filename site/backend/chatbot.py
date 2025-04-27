from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from React

# Define the Rasa server URL
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"


@app.route("/chat", methods=["POST"])
def chat():
    # Get user message from the request body
    user_message = request.json.get("message")
    sender_id = request.json.get("sender", "default_user")  # Default sender ID

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Forward the message to the Rasa server
        response = requests.post(
            RASA_URL, json={"sender": sender_id, "message": user_message})

        if response.status_code == 200:
            # Return the Rasa response to the client
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to connect to Rasa", "details": response.text}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
