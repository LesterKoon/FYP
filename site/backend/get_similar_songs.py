from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import numpy as np
import os
import time
import threading

app = Flask(__name__)
CORS(app)

# Global variables to store the latest emotions and similar songs
latest_emotions = {}
similar_songs = []


def find_similar_songs_cosine(target_emotion_values):
    db_path = os.path.join(os.path.dirname(__file__),
                           '../database/vibesync.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query all songs with their emotion values and Spotify URI
    cursor.execute(
        "SELECT ROWID, Sp_URI, Happy, Excited, Energetic, Fear, Sad, Depressed, Calm, Angry FROM songs")
    songs = cursor.fetchall()

    # Convert target emotion values to a numpy array
    target_emotion_vector = np.array(target_emotion_values)

    # Calculate cosine similarity for each song
    similarities = []
    for song in songs:
        sp_uri = song[1]
        emotion_vector = np.array(song[2:])

        numerator = np.dot(target_emotion_vector, emotion_vector)
        denominator = np.linalg.norm(
            target_emotion_vector) * np.linalg.norm(emotion_vector)
        similarity = numerator / denominator if denominator != 0 else 0
        similarities.append((sp_uri, similarity))

    # Sort by similarity (higher is better)
    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)

    # Get the top 5 most similar songs
    most_similar_songs = [sp_uri for sp_uri, _ in similarities[:5]]
    conn.close()
    return most_similar_songs


def update_similar_songs_periodically():
    global latest_emotions, similar_songs

    while True:
        if latest_emotions:
            # Convert emotions to a list
            target_emotion_values = [
                latest_emotions.get("Happy", 0.0),
                latest_emotions.get("Excited", 0.0),
                latest_emotions.get("Energetic", 0.0),
                latest_emotions.get("Fear", 0.0),
                latest_emotions.get("Sad", 0.0),
                latest_emotions.get("Depressed", 0.0),
                latest_emotions.get("Calm", 0.0),
                latest_emotions.get("Angry", 0.0),
            ]

            # Find similar songs
            similar_songs = find_similar_songs_cosine(target_emotion_values)
            print("Updated similar songs:", similar_songs)
        else:
            print("No emotions detected yet.")

        # Wait 5 seconds before updating again
        time.sleep(5)


@app.route('/update_emotions', methods=['POST'])
def update_emotions():
    global latest_emotions
    latest_emotions = request.json  # Update latest emotions
    return jsonify({"status": "success", "data": latest_emotions})


@app.route('/get_emotions', methods=['GET'])
def get_emotions():
    return jsonify({"status": "success", "data": latest_emotions})


@app.route('/get_similar_songs', methods=['GET'])
def get_similar_songs():
    return jsonify(similar_songs)


if __name__ == "__main__":
    # Start the periodic update thread
    threading.Thread(target=update_similar_songs_periodically, daemon=True).start()
    app.run(port=5006)
