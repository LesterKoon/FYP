import React from 'react';
import { ParallaxProvider, Parallax } from 'react-scroll-parallax';
import './page.css';

const Home = () => {
    return (
        <div className="home">
            <ParallaxProvider>
                <div className="parallax-container">
                    <Parallax 
                        className="parallax-background" 
                        speed={5} translateY={[-20, 20]}
                    >
                        <div className="background" />
                    </Parallax>

                    <div className="text-container">
                        <Parallax speed={30} translateY={[30, -30]}>
                            <div className="parallax-text">
                                <h1>Welcome to VibeSync</h1>
                                <p>An AI-driven music recommendation system that understands <br></br>
                                your emotions and mood.<br></br>
                                Explore music in a whole new way!</p>
                                <a href="http://localhost:3000/chatbot"  className="start-button">
                                    Get Started
                                </a>
                            </div>
                        </Parallax>
                    </div>
                </div>

                <section className="features-section">
                    <div className="features-container">
                        <h2>Discover The Track Perfect For Your Mood</h2>
                        <div className="features-grid">
                            <div className="feature-card">
                                <h3>Emotion-Based Recommendations</h3>
                                <p>Explore a curated collection of emotion-classified music, where tracks are thoughtfully organized by their mood.</p>
                            </div>
                            
                            <div className="feature-card">
                                <h3>Integrated Chatbot</h3>
                                <p>Engage with an advanced AI-powered chatbot that intuitively understands your feelings and curates music to match your vibe.</p>
                            </div>
                            
                            <div className="feature-card">
                                <h3>Real-time Adaptation</h3>
                                <p>Seamlessly adapt to your activities and environment with contextual music suggestions, as your feeling changes, so does the music.</p>
                            </div>
                        </div>
                    </div>
                </section>
            </ParallaxProvider>
        </div>
    );
};

export default Home;