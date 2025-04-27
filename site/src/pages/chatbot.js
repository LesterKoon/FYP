import React, { useState, useEffect, useRef } from "react";
import { Container, Row, Col } from "react-bootstrap";
import axios from "axios";
import "./page.css";
import SpotifyEmbed from '../components/SpotifyEmbed';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Chatbot = () => {
  const [messages, setMessages] = useState([]); 
  const [input, setInput] = useState(""); 
  const [loading, setLoading] = useState(false);
  const [dots, setDots] = useState(""); 

  const isInitialized = useRef(false);
  const chatBoxRef = useRef(null); 

  const [trackIds, setTrackIds] = useState([]); // To store original track URIs
  const [formattedTrackIds, setFormattedTrackIds] = useState([]); // To store stripped URIs for embeds
  const [emotions, setEmotions] = useState(null); // State for emotion data
  
// Chatbot functions
  const sendMessage = async (message) => {
    if (!message.trim()) return;

    setMessages((prev) => [...prev, { sender: "user", text: message }]);
    setLoading(true); // Show loading indicator

    try {
      const response = await axios.post("http://localhost:5005/webhooks/rest/webhook", {
        message: message,
      });

      if (response.data && response.data.length > 0) {
        setMessages((prev) => [
          ...prev,
          { sender: "bot", text: response.data[0].text },
        ]);
      }
    } catch (error) {
      console.error("Error communicating with chatbot:", error);
    }

    setLoading(false); 
    setInput(""); 
  };

  // Fetch emotions
  const fetchEmotions = async () => {
    try {
      const response = await fetch('http://localhost:5006/get_emotions');
      if (response.ok) {
        const data = await response.json();
        setEmotions(data.data); // Store emotion data
      } else {
        console.error('Failed to fetch emotions:', response.status);
      }
    } catch (error) {
      console.error('Error fetching emotions:', error);
    }
  };

  const scrollToBottom = () => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  };

  // Song display functions
  const fetchSimilarSongs = async () => {
    try {
      const response = await fetch('http://localhost:5006/get_similar_songs');
      if (response.ok) {
        const data = await response.json();

        setTrackIds(data);

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
          playlist_name: 'Your VibeSync Playlist',
        }),
      });

      const data = await response.json();
      if (response.ok) {
        alert(`Playlist created! Check it out here: ${data.playlist_link}`)
        window.open(data.playlist_link, '_blank');
      } else {
        console.error('Failed to create playlist:', data.error);
      }
    } catch (error) {
      console.error('Error saving playlist:', error);
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, dots]);

  useEffect(() => {
    if (loading) {
      const interval = setInterval(() => {
        setDots((prev) => (prev.length < 3 ? prev + "." : ""));
      }, 400); 
      return () => clearInterval(interval); 
    } else {
      setDots(""); 
    }
  }, [loading]);

  useEffect(() => {
    if (!isInitialized.current) {
      const initializeChat = async () => {
        try {
          const response = await axios.post("http://localhost:5005/webhooks/rest/webhook", {
            sender: "test_user",
            message: "Hello",
          });

          if (response.data && response.data.length > 0) {
            setMessages((prev) => [
              ...prev,
              { sender: "bot", text: response.data[0].text },
            ]);
          }
        } catch (error) {
          console.error("Error initializing chat:", error);
        }
      };

      initializeChat();
      isInitialized.current = true;
    }

    // Initialize music player
    fetchSimilarSongs();
    fetchEmotions();
    const interval = setInterval(() => {
      fetchSimilarSongs();
      fetchEmotions(); // Fetch emotions on the same interval
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const renderEmotionGraph = () => {
  if (!emotions) return null;

  const EMOTION_COLORS = {
    Angry: '#ff4d4d',     // Red
    Calm: '#4db8ff',      // Light Blue
    Depressed: '#808080', // Gray
    Energetic: '#ffdb4d', // Yellow
    Excited: '#ff944d',   // Orange  
    Fear: '#9933ff',      // Purple
    Happy: '#66ff66',     // Green
    Sad: '#4d4dff'        // Blue
  };

  const data = Object.entries(emotions).map(([name, value]) => ({
    name,
    value: Math.round(value * 100),
    fill: EMOTION_COLORS[name]
  }));

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f5f5f5" />
        <XAxis dataKey="name" stroke="#666" />
        <YAxis stroke="#666" />
        <Tooltip 
          formatter={(value) => [`${value}%`, "Intensity"]}
          contentStyle={{
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            border: '1px solid #ccc',
            borderRadius: '4px'
          }}
        />
        <Bar 
          dataKey="value" 
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
  };


  return (
    <div className="chatbot">
      <Container fluid className="chatbot-container">
        <Row className="chatbot-row align-items-center justify-content-start">
          <Col xs={12} md={6} className="d-flex justify-content-center">
            <div className="chat-window">
              <div className="header">Interested in VibeSync?</div>
              <div className="chatBox" ref={chatBoxRef}>
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`message-container ${
                      msg.sender === "user" ? "user-message" : "bot-message"
                    }`}
                  >
                    {msg.sender === "bot" && (
                      <img
                        src="/assets/icon_dark.png" // Replace with the actual image path
                        alt="Bot Avatar"
                        className="bot-avatar"
                      />
                    )}
                    <div
                      className={`message ${
                        msg.sender === "user" ? "userMessage" : "botMessage"
                      }`}
                    >
                      {msg.text}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="message-container bot-message">
                    <img
                      src="/assets/icon_dark.png"
                      alt="Bot Avatar"
                      className="bot-avatar"
                    />
                    <div className="message botMessage">Typing{dots}</div>
                  </div>
                )}
              </div>
              <div className="inputArea">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && sendMessage(input)}
                  placeholder="Type your response..."
                  className="input"
                />
                <button onClick={() => sendMessage(input)} className="sendButton">
                  ⮚
                </button>
              </div>
            </div>
          </Col>

          <Col xs={12} md={6} className="song-container">
            <div className="song-display">
              <h2>Recommended Songs:</h2>
              <div className="songs space-y-4">
                {formattedTrackIds.length > 0 ? (
                  formattedTrackIds.map((trackId, index) => (
                    <SpotifyEmbed
                      key={`${trackId}-${index}`}
                      trackId={trackId}
                      title={`Track ${index + 1}`}
                      width= '100%'
                      height= '80px'
                    />
                  ))
                ) : (
                  <p className="text-gray-500">No tracks to display. Please wait...</p>
                )}
              </div>
              {formattedTrackIds.length > 0 && (
                <div className="save">
                  <button
                    onClick={savePlaylist}
                    className="save-button"
                  >
                    Save Playlist
                  </button>
                </div>
              )}
            </div>
          </Col>
        </Row>
        <Row>
          <Col xs={12} className="emotion-graph">
            <h3>Emotion Analysis:</h3>
            {renderEmotionGraph()}
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default Chatbot;
