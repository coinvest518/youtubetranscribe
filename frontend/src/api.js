// src/api.js
import express from 'express';
import fetch from 'node-fetch';

const router = express.Router();

router.post('/transcribe', async (req, res) => {
  const { url } = req.body;

  if (!url) {
    return res.status(400).json({ error: 'No URL provided' });
  }

  try {
    // Step 1: Start the transcription
    const transcriptResponse = await fetch('https://api.assemblyai.com/v2/transcript', {
      method: 'POST',
      headers: {
        Authorization: process.env.ASSEMBLY_AI_API_KEY,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ audio_url: url }),
    });

    if (!transcriptResponse.ok) {
      throw new Error('Failed to start transcription');
    }

    const transcriptData = await transcriptResponse.json();

    // Step 2: Poll for the transcription result
    let isTranscribing = true;
    let result;

    while (isTranscribing) {
      const statusResponse = await fetch(`https://api.assemblyai.com/v2/transcript/${transcriptData.id}`, {
        headers: {
          Authorization: process.env.ASSEMBLY_AI_API_KEY,
        },
      });

      const statusData = await statusResponse.json();

      if (statusData.status === 'completed') {
        result = statusData.text;
        isTranscribing = false;
      } else if (statusData.status === 'error') {
        throw new Error('Transcription failed');
      }

      // Wait for 3 seconds before polling again
      await new Promise((resolve) => setTimeout(resolve, 3000));
    }

    res.json({ transcription: result });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});

export default router;
