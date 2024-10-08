import React, { useState } from 'react';
import axios from 'axios';

const DownloadForm = () => {
    const [youtubeUrl, setYoutubeUrl] = useState('');
    const [message, setMessage] = useState('');
    const [transcription, setTranscription] = useState('');

    const handleDownload = async (e) => {
        e.preventDefault();
        setMessage('');
        setTranscription('');

        try {
            // Step 1: Download the audio
            const downloadResponse = await axios.post('http://localhost:5000/download', { youtube_url: youtubeUrl });
            setMessage(downloadResponse.data.message);
            const fileName = downloadResponse.data.file;

            // Step 2: Start transcription
            const transcribeResponse = await axios.post('http://localhost:5000/transcribe', { file_name: fileName });
            const id = transcribeResponse.data.transcript_id; // Use a local variable instead
            setMessage('Transcription in progress...');

            // Step 3: Poll for transcription result
            pollTranscriptionResult(id); // Pass the local variable to the polling function
        } catch (error) {
            setMessage(`Error: ${error.response ? error.response.data.error : error.message}`);
        }
    };

    const pollTranscriptionResult = async (id) => {
        const interval = setInterval(async () => {
            try {
                const resultResponse = await axios.get(`http://localhost:5000/transcription_result/${id}`);
                if (resultResponse.data.status === 'completed') {
                    clearInterval(interval);
                    setTranscription(resultResponse.data.text);
                    setMessage('Transcription completed successfully.');
                } else if (resultResponse.data.status === 'failed') {
                    clearInterval(interval);
                    setMessage('Transcription failed.');
                }
            } catch (error) {
                clearInterval(interval);
                setMessage('Error fetching transcription result.');
            }
        }, 5000); // Poll every 5 seconds
    };

    return (
        <div>
            <form onSubmit={handleDownload}>
                <input
                    type="text"
                    value={youtubeUrl}
                    onChange={(e) => setYoutubeUrl(e.target.value)}
                    placeholder="Enter YouTube URL"
                    required
                />
                <button type="submit">Download and Transcribe</button>
            </form>
            {message && <p>{message}</p>}
            {transcription && (
                <div>
                    <h3>Transcription:</h3>
                    <p>{transcription}</p>
                </div>
            )}
        </div>
    );
};

export default DownloadForm;
