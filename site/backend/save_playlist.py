from flask import Flask, request, jsonify
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
CORS(app)

# Spotify API credentials
SPOTIPY_CLIENT_ID = 'f304455c10134fdab7ec8dec0f1240d8'
SPOTIPY_CLIENT_SECRET = 'c33cb08e991f479a9f8c36f8a9c12420'
SPOTIPY_REDIRECT_URI = 'http://localhost:5001'

# Initialize Spotipy with user authorization
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="playlist-modify-public",
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI
))


def save_to_spotify_playlist(track_uris, playlist_name="Your VibeSync Playlist"):
    try:
        # Get the current user's ID
        user_id = sp.me()["id"]

        # Create a new playlist
        playlist = sp.user_playlist_create(
            user=user_id, name=playlist_name, public=True)
        playlist_id = playlist["id"]

        # Add tracks to the playlist
        sp.playlist_add_items(playlist_id, track_uris)

        print(
            f"Playlist '{playlist_name}' created and songs added successfully!")
        return playlist["external_urls"]["spotify"]
    except Exception as e:
        print(f"Error creating playlist: {e}")
        return None


@app.route('/save_playlist', methods=['POST'])
def save_playlist():
    try:
        # Parse JSON body for track URIs and playlist name
        data = request.json
        track_uris = data.get("track_uris", [])
        playlist_name = data.get("playlist_name", "Your VibeSync Playlist")

        if not track_uris:
            return jsonify({"error": "No track URIs provided"}), 400

        # Save the playlist
        playlist_link = save_to_spotify_playlist(track_uris, playlist_name)

        if playlist_link:
            return jsonify({"message": "Playlist created", "playlist_link": playlist_link}), 200
        else:
            return jsonify({"error": "Failed to create playlist"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5002)
