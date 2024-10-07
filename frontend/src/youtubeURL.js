// src/YouTubeURLInput.js
import React, { useState } from 'react';
import './App.css';

const YouTubeURLInput = ({ onSubmit }) => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  const extractVideoID = (videoURL) => {
    const regExp = /^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/)([^#&?]*).*/;
    const match = videoURL.match(regExp);
    return (match && match[1]?.length === 11) ? match[1] : null;
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const videoId = extractVideoID(url);
    if (!videoId) {
      setError('Invalid YouTube URL');
      return;
    }
    setError('');
    onSubmit(videoId);
    setUrl('');
  };

  return (
    <form className="url-input-form" onSubmit={handleSubmit}>
      <input
        type="url"
        placeholder="Enter YouTube Video URL"
        value={url}
        onChange={(e) => {
          setUrl(e.target.value);
          setError('');
        }}
        required
        className="url-input"
      />
      <button type="submit" className="submit-button">Get Audio</button>
      {error && <div className="error-message">{error}</div>}
    </form>
  );
};

export default YouTubeURLInput;
