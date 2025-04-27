from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

def get_random_songs_by_quadrant(quadrant):
    try:
        db_path = os.path.join(os.path.dirname(
            __file__), '../database/billboard_top.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query random songs from specified emotion quadrant
        cursor.execute("""
            SELECT Sp_URI 
            FROM songs 
            WHERE Emotion_Quadrant = ?
            ORDER BY RANDOM() 
            LIMIT 20
        """, (quadrant,))

        songs = cursor.fetchall()
        random_songs = [song[0] for song in songs]

        return random_songs

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        if conn:
            conn.close()


@app.route('/get_songs_by_emotion', methods=['GET'])
def get_songs_by_emotion():
    # Get emotion quadrant from query parameter
    emotion_quadrant = request.args.get('quadrant')

    if not emotion_quadrant:
        return jsonify({'error': 'Emotion quadrant parameter is required'}), 400

    songs = get_random_songs_by_quadrant(emotion_quadrant)

    if not songs:
        return jsonify({'error': 'No songs found for this emotion quadrant'}), 404

    return jsonify(songs)


if __name__ == '__main__':
    app.run(port=5004)
