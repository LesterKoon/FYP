import React from 'react';

const SpotifyEmbed = ({ trackId, width, height = "352" }) => {
    return (
    <iframe
        title={`Spotify Embed - ${trackId}`}
        style={{ borderRadius: "12px" }}
        src={`https://open.spotify.com/embed/track/${trackId}?utm_source=generator`}
        width={width}
        height={height}
        allowFullScreen=""
        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
        loading="lazy"
    />
    );
};

export default SpotifyEmbed;