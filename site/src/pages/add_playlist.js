import React, { useState, useEffect, useRef } from 'react';
import { Container, Card, Form, Button, Alert, Spinner} from 'react-bootstrap';
import gsap from 'gsap';
import { ReactComponent as BackgroundSVG } from '../components/Music.svg';
import 'bootstrap/dist/css/bootstrap.min.css';
import './page.css';

const AddPlaylist = () => {
  const [playlistUrl, setPlaylistUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState(null);

  // Refs for SVG instances
  const svg1 = useRef(null);
  const svg2 = useRef(null);
  const svg3 = useRef(null);

  useEffect(() => {
    // Different animations for each instance
    gsap.to(svg1.current, {
      x: "random(-50, 50)",
      y: "random(-50, 100)",
      rotation: 360,
      duration: 20,
      repeat: -1,
      ease: "none"
    });

    gsap.to(svg2.current, {
      x: "random(-50, 50)",
      y: "random(-50, 50)",
      rotation: -360,
      duration: 25,
      repeat: -1,
      ease: "none"
    });

    gsap.to(svg3.current, {
      x: "random(-50, 50)",
      y: "random(-50, 100)",
      rotation: "random(-360, 360)",
      duration: 22,
      repeat: -1,
      ease: "none"
    });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsProcessing(true);
    setError('');
    setResults(null);

    try {
      const response = await fetch('http://localhost:5003/process_playlist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ playlist_url: playlistUrl }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to process playlist');
      }

      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const renderTrackStatus = (track) => {
    if (track.error) {
      return <Alert variant="danger">Error processing track: {track.error}</Alert>;
    }
    
    if (track.status) {
      return <Alert variant="warning">{track.status}</Alert>;
    }

    return <Alert variant="success">{track.track_name} has been added to the database</Alert>;
  };

  return (
    <div className="add_playlist">
        <div className="background-svg svg1" ref={svg1}>
            <BackgroundSVG />
        </div>
        <div className="background-svg svg2" ref={svg2}>
            <BackgroundSVG />
        </div>
        <div className="background-svg svg3" ref={svg3}>
            <BackgroundSVG />
        </div>
        <div className="processor-page">
        <Container className="playlist-processor">
            <Card className="main-card">
            <Card.Header className="text-center">
                <Card.Title className="mb-0">Process Spotify Playlist</Card.Title>
            </Card.Header>
            <Card.Body>
                <Form onSubmit={handleSubmit} className="playlist-form">
                <Form.Group>
                    <Form.Control
                    type="text"
                    placeholder="Enter Spotify playlist URL"
                    value={playlistUrl}
                    onChange={(e) => setPlaylistUrl(e.target.value)}
                    disabled={isProcessing}
                    className="url-input"
                    />
                </Form.Group>
                <Button 
                    type="submit" 
                    variant="primary"
                    disabled={isProcessing || !playlistUrl}
                    className="submit-button"
                >
                    {isProcessing ? (
                    <>
                        <Spinner
                        as="span"
                        animation="border"
                        size="sm"
                        role="status"
                        aria-hidden="true"
                        className="spinner"
                        />
                        Processing...
                    </>
                    ) : (
                    'Process Playlist'
                    )}
                </Button>
                </Form>

                {error && (
                <Alert variant="danger" className="error-alert">
                    {error}
                </Alert>
                )}

                {results && (
                <div className="results-container">
                    <h4 className="text-center mb-4">Processed Tracks</h4>
                    <div className="tracks-list">
                    {results.processed_tracks.map((track, index) => (
                        <div key={index} className="track-result">
                        {renderTrackStatus(track)}
                        </div>
                    ))}
                    </div>
                </div>
                )}
            </Card.Body>
            </Card>
        </Container>
        </div>
    </div>
  );
};

export default AddPlaylist;