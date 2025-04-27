from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import librosa
import numpy as np
import os
import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)
CORS(app)

# Constants
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
DATABASE = os.path.join(os.path.dirname(__file__), '../database/vibesync.db')

# Spotify API Credentials
CLIENT_ID = 'f304455c10134fdab7ec8dec0f1240d8'
CLIENT_SECRET = 'c33cb08e991f479a9f8c36f8a9c12420'

linguistic_bins = {
    "Intensity": {"Very Low": (0, 0.0938), "Low": (0.0938, 0.1462), "Medium": (0.1462, 0.1955), "High": (0.1955, 0.2451), "Very High": (0.2451, 1)},
    "Timbre": {"Very Low": (-100, -6.8848), "Low": (-6.8848, -1.2937), "Medium": (-1.2937, 2.4315), "High": (2.4315, 6.0919), "Very High": (6.0919, 100)},
    "Pitch": {"Very Low": (0, 810.1318), "Low": (810.1318, 1011.7241), "Medium": (1011.7241, 1195.7592), "High": (1195.7592, 1421.4669), "Very High": (1421.4669, 5000)},
    "Rhythm": {"Very Low": (0, 95.7031), "Low": (95.7031, 112.3471), "Medium": (112.3471, 129.1992), "High": (129.1992, 143.5547), "Very High": (143.5547, 500)}
}

# Emotion table
emotion_table = {
    "Happy": {"Intensity": "Medium", "Timbre": "Medium", "Pitch": "Very High", "Rhythm": "Very High"},
    "Excited": {"Intensity": "High", "Timbre": "Medium", "Pitch": "High", "Rhythm": "High"},
    "Energetic": {"Intensity": "Very High", "Timbre": "Medium", "Pitch": "Medium", "Rhythm": "High"},
    "Fear": {"Intensity": "High", "Timbre": "High", "Pitch": "Very High", "Rhythm": "Very High"},
    "Sad": {"Intensity": "Medium", "Timbre": "Very Low", "Pitch": "Very Low", "Rhythm": "Low"},
    "Depressed": {"Intensity": "Low", "Timbre": "Low", "Pitch": "Low", "Rhythm": "Low"},
    "Calm": {"Intensity": "Very Low", "Timbre": "Very Low", "Pitch": "Medium", "Rhythm": "Very Low"},
    "Angry": {"Intensity": "Very High", "Timbre": "Very High", "Pitch": "Medium", "Rhythm": "Very High"}
}



# Ensure download folder exists
def ensure_download_folder():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

# Extract tracks from Spotify playlist
def get_playlist_tracks(playlist_url):
    auth_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    try:
        # Extract playlist ID
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        results = sp.playlist_tracks(playlist_id)
        tracks = results['items']

        # Prepare track list
        track_list = []
        for track in tracks:
            track_uri = track['track']['uri']
            track_list.append({'uri': track_uri})

        return track_list
    except Exception as e:
        return f"Error: {e}"
    
def check_uri_exists(spotify_uri):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT sp_uri FROM songs WHERE sp_uri = ?", (spotify_uri,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def calculate_proximity(value, target_bin, feature_bins):
    lower, upper = feature_bins[target_bin]
    range_size = upper - lower
    if lower <= value <= upper:
        return 1.0
    elif value < lower:
        return max(0, 1 - (lower - value) / range_size)
    else:
        return max(0, 1 - (value - upper) / range_size)


def calculate_emotion_weights(intensity, timbre, pitch, rhythm, salience_boost=5.0):
    input_features = {
        "Intensity": intensity,
        "Timbre": timbre,
        "Pitch": pitch,
        "Rhythm": rhythm
    }

    emotion_weights = {}
    for emotion, conditions in emotion_table.items():
        total_weight = 0
        for feature, target_bin in conditions.items():
            feature_value = input_features[feature]
            weight = calculate_proximity(
                feature_value, target_bin, linguistic_bins[feature])
            total_weight += weight
        raw_weight = total_weight / 4.0
        boosted_weight = raw_weight**salience_boost
        emotion_weights[emotion] = boosted_weight

    total_score = sum(emotion_weights.values())
    if total_score > 0:
        for emotion in emotion_weights:
            emotion_weights[emotion] = round(emotion_weights[emotion] / total_score, 4)
    return emotion_weights


def save_song_to_db(song_data):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO songs (
            sp_uri, track_name, intensity, timbre, pitch, rhythm,
            happy, excited, energetic, fear, 
            sad, depressed, calm, angry
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        song_data['spotify_uri'],
        song_data['track_name'],
        song_data['intensity'],
        song_data['timbre'],
        song_data['pitch'],
        song_data['rhythm'],
        song_data.get('Happy', 0),
        song_data.get('Excited', 0),
        song_data.get('Energetic', 0),
        song_data.get('Fear', 0),
        song_data.get('Sad', 0),
        song_data.get('Depressed', 0),
        song_data.get('Calm', 0),
        song_data.get('Angry', 0)
    ))

    conn.commit()
    conn.close()

# Route: Extract playlist
@app.route('/extract_playlist', methods=['POST'])
def extract_playlist():
    try:
        data = request.json
        playlist_url = data.get('playlist_url')

        if not playlist_url:
            return jsonify({'error': 'Playlist URL is required'}), 400

        # Extract tracks
        tracks = get_playlist_tracks(playlist_url)

        if isinstance(tracks, str) and 'Error' in tracks:
            return jsonify({'error': tracks}), 500

        return jsonify({'tracks': tracks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Download song and extract features
@app.route('/download', methods=['POST'])
def download_song():
    ensure_download_folder()

    try:
        data = request.json
        spotify_uri = data.get('spotify_uri')

        if not spotify_uri:
            return jsonify({'error': 'Spotify URI is required'}), 400

        # Convert URI to track URL
        track_url = f"https://open.spotify.com/track/{spotify_uri.split(':')[-1]}"

        # Use spotdl to download the song
        command = ['spotdl', track_url, '--output', DOWNLOAD_DIR]
        subprocess.run(command, check=True)

        # Find downloaded file
        files = os.listdir(DOWNLOAD_DIR)
        downloaded_file = next((f for f in files if f.endswith('.mp3')), None)

        if not downloaded_file:
            return jsonify({'error': 'Download failed'}), 500

        file_path = os.path.join(DOWNLOAD_DIR, downloaded_file)
        
        # Extract track name from file
        track_name = os.path.splitext(os.path.basename(file_path))[0]

        # Extract features
        y, sr = librosa.load(file_path, sr=None)
        
        rms = librosa.feature.rms(y=y)
        intensity = float(np.mean(rms).item())

        # Convert MFCCs to native Python float
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        timbre = float(np.mean(mfccs).item())

        # Convert pitch to native Python float
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = pitches[pitches > 0]
        pitch = float(np.mean(pitch_values).item()) if len(
            pitch_values) > 0 else 0.0

        # Convert tempo to native Python float, with proper type checking
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        rhythm = float(tempo) if np.isscalar(tempo) else tempo.item()
        
        emotions = calculate_emotion_weights(intensity, timbre, pitch, rhythm)

        # Clean up downloaded file
        os.remove(file_path)

        return jsonify({
            'track_name': track_name,
            'intensity': intensity,
            'timbre': timbre,
            'pitch': pitch,
            'rhythm': rhythm,
            **emotions
        })

    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Failed to download the song. Check the Spotify URI.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route: Process entire playlist


@app.route('/process_playlist', methods=['POST'])
def process_playlist():
    try:
        data = request.json
        playlist_url = data.get('playlist_url')

        if not playlist_url:
            return jsonify({'error': 'Playlist URL is required'}), 400

        # Extract tracks
        tracks = get_playlist_tracks(playlist_url)

        if isinstance(tracks, str) and 'Error' in tracks:
            return jsonify({'error': tracks}), 500

        processed_tracks = []
        for track in tracks:
            spotify_uri = track['uri']
            
            # Check if URI already exists in database
            if check_uri_exists(spotify_uri):
                processed_tracks.append({
                    "spotify_uri": spotify_uri,
                    "status": "skipped - already exists in database"
                })
                continue

            # Simulate calling the /download logic directly
            try:
                features = download_song_from_uri(spotify_uri)

                processed_track = {
                    "spotify_uri": spotify_uri,
                    "track_name": features.get("track_name", ""),
                    "intensity": features.get("intensity", 0),
                    "timbre": features.get("timbre", 0),
                    "pitch": features.get("pitch", 0),
                    "rhythm": features.get("rhythm", 0),
                }
                # Add emotion values directly to the track object
                for emotion, value in features.items():
                    if emotion not in ["intensity", "timbre", "pitch", "rhythm"]:
                        processed_track[emotion] = value
                        
                save_song_to_db(processed_track)
                processed_tracks.append(processed_track)
                
            except Exception as e:
                processed_tracks.append({
                    "spotify_uri": spotify_uri,
                    "error": str(e)
                })

        return jsonify({"processed_tracks": processed_tracks})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def download_song_from_uri(spotify_uri):
    try:
        data = {'spotify_uri': spotify_uri}

        with app.test_request_context(json=data):
            # Call the /download logic
            response = download_song()

            # If it's a tuple (response, status_code), handle it
            if isinstance(response, tuple):
                response = response[0]

            # Extract JSON data
            result = response.get_json()

            response_data = {
                "track_name": result.get("track_name", ""),
                "intensity": result.get("intensity", 0),
                "timbre": result.get("timbre", 0),
                "pitch": result.get("pitch", 0),
                "rhythm": result.get("rhythm", 0)
            }

            # Add emotion values
            for key in ["Happy", "Excited", "Energetic", "Fear", "Sad", "Depressed", "Calm", "Angry"]:
                if key in result:
                    response_data[key] = result[key]

            return response_data
    except Exception as e:
        return {"error": str(e)}


if __name__ == '__main__':
    ensure_download_folder()
    app.run(port=5003, debug=True)
