import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AppNavbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/home';
import Chatbot from './pages/chatbot';
import AddPlaylist from './pages/add_playlist';
import Explore from './pages/explore';
import About from './pages/about';

// Add global styles for consistency across pages
import './App.css';

const App = () => {
    return (
       <div className="App">
        <Router>
              <AppNavbar />
              <div className="app-content">
                  <Routes>
                      <Route path="/" element={<Home />} />
                      <Route path="/chatbot" element={<Chatbot />} />
                      <Route path="/add-playlist" element={<AddPlaylist />} />
                      <Route path="/explore" element={<Explore />} />
                  </Routes>
              </div>
              <Footer />
          </Router>
        </div>
    );
};

export default App;
