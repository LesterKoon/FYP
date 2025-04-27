import React, { useState, useEffect } from 'react';
import { Container, Row, Carousel } from 'react-bootstrap';
import SpotifyEmbed from '../components/SpotifyEmbed';
import 'bootstrap/dist/css/bootstrap.min.css';
import bg1 from '../components/bg1.jpg';
import bg2 from '../components/bg2.jpg';
import bg3 from '../components/bg3.jpg';
import bg4 from '../components/bg4.jpg';
import './page.css';

const Explore = () => {
  const [activeQuadrant, setActiveQuadrant] = useState('1');
  const [tracks, setTracks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const emotions = [
    { id: '1', name: 'High Energy, Positive', subtitle: 'Excitement, Joy, Enthusiasm', image: bg1 },
    { id: '2', name: 'High Energy, Negative', subtitle: 'Anger, Fear, Frustration', image: bg2 },
    { id: '3', name: 'Low Energy, Negative', subtitle: 'Sadness, Disappointment, Depression', image: bg3 },
    { id: '4', name: 'Low Energy, Positive', subtitle: 'Contentment, Calm, Relaxation', image: bg4 }
  ];

  const fetchSongsByEmotion = async (quadrant) => {
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:5004/get_songs_by_emotion?quadrant=${quadrant}`);
      if (response.ok) {
        const data = await response.json();
        setTracks(data.map(uri => uri.replace('spotify:track:', '')));
      }
    } catch (error) {
      console.error('Error fetching songs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = (selectedIndex) => {
    const newQuadrant = String(selectedIndex + 1);
    setActiveQuadrant(newQuadrant);
    fetchSongsByEmotion(newQuadrant);
  };

  useEffect(() => {
    fetchSongsByEmotion(activeQuadrant);
  }, [activeQuadrant]);

  return (
    <div className="explore">
        <div className="page-container">
        {/* Top Section */}
        <div className="carousel-wrapper">
            <Carousel
            activeIndex={Number(activeQuadrant) - 1}
            onSelect={handleSelect}
            interval={null}
            indicators={false}
            controls={true} 
            >
            {emotions.map((emotion) => (
                <Carousel.Item key={emotion.id}>
                    <div 
                        className="emotion-slide"
                        style={{
                        backgroundImage: `url(${emotion.image})`,
                        }}
                    >
                        <div className="emotion-overlay">
                        <h2 className="emotion-title">
                            {emotion.name}
                        </h2>
                        <p className="emotion-subtitle">
                            {emotion.subtitle}
                        </p>
                        </div>
                    </div>
                </Carousel.Item>
            ))}
            </Carousel>
        </div>

        {/* Bottom Section */}
        <div className="songs-section">
            {isLoading ? (
            <div className="loading">Loading songs...</div>
            ) : (
            <Container fluid>
                <Row className="songs-grid">
                {tracks.map((trackId, index) => (
                    <SpotifyEmbed
                    key={`${trackId}-${index}`}
                    trackId={trackId}
                    title={`Track ${index + 1}`}
                    height='100px'
                    />
                ))}
                </Row>
            </Container>
            )}
        </div>
        </div>
    </div>
  );
};

export default Explore;