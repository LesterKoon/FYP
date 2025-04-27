import React, { useState, useEffect } from 'react';
import SpotifyEmbed from './components/SpotifyEmbed';

const App = () => {
  const [trackIds, setTrackIds] = useState([]); // To store original track URIs
  const [formattedTrackIds, setFormattedTrackIds] = useState([]); // To store stripped URIs for embeds

  const fetchSimilarSongs = async () => {
    try {
      const response = await fetch('http://localhost:5006/get_similar_songs');
      if (response.ok) {
        const data = await response.json();

        // Preserve the original list of URIs
        setTrackIds(data);

        // Create a new list with 'spotify:track:' stripped
        const strippedTrackIds = data.map((uri) => uri.replace('spotify:track:', ''));
        setFormattedTrackIds(strippedTrackIds);

        console.log("Raw Track URIs from API:", data);
        console.log("Formatted Track IDs for Embed:", strippedTrackIds);
      } else {
        console.error('Failed to fetch similar songs:', response.status);
      }
    } catch (error) {
      console.error('Error fetching similar songs:', error);
    }
  };

  const savePlaylist = async () => {
    try {
      const response = await fetch('http://localhost:5002/save_playlist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          track_uris: trackIds,
          playlist_name: 'My React Playlist',
        }),
      });

      const data = await response.json();
      if (response.ok) {
        alert(`Playlist created! Check it out here: ${data.playlist_link}`);
      } else {
        console.error('Failed to create playlist:', data.error);
      }
    } catch (error) {
      console.error('Error saving playlist:', error);
    }
  };

  useEffect(() => {
    fetchSimilarSongs(); // Fetch immediately on load

    const interval = setInterval(() => {
      fetchSimilarSongs(); // Fetch every 5 seconds to sync with Flask
    }, 5000);

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-3xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            My Music Player
          </h1>
          <p className="text-gray-600">Listen to your favorite tracks</p>
        </header>

        <main className="bg-white rounded-lg shadow-lg p-6">
          <div className="space-y-6">
            {formattedTrackIds.length > 0 ? (
              formattedTrackIds.map((trackId, index) => (
                <SpotifyEmbed
                  key={`${trackId}-${index}`}
                  trackId={trackId}
                  title={`Track ${index + 1}`}
                />
              ))
            ) : (
              <p className="text-gray-500">No tracks to display. Please wait...</p>
            )}
          </div>

          {/* Save Playlist Button */}
          {formattedTrackIds.length > 0 && (
            <button
              onClick={savePlaylist}
              className="mt-4 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            >
              Save Playlist
            </button>
          )}
        </main>

        <footer className="mt-8 text-center text-gray-600">
          <p>&copy; 2024 My Music Player. All rights reserved.</p>
        </footer>
      </div>
    </div>
  );
};

export default App;
