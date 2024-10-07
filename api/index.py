from flask import Flask, request, jsonify, send_from_directory # type: ignore
from flask_cors import CORS # type: ignore
import os
import logging
from dotenv import load_dotenv # type: ignore
import requests # type: ignore
from yt_dlp import YoutubeDL # type: ignore

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up yt-dlp options
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'api/downloads/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'noplaylist': True,
}

# Ensure the downloads directory exists
if not os.path.exists('api/downloads'):
    os.makedirs('api/downloads')

# Fetch the API key from environment variables
ASSEMBLY_AI_API_KEY = os.getenv('ASSEMBLY_AI_API_KEY')

@app.route('api/download', methods=['POST'])
def download_audio():
    youtube_url = request.json.get('youtube_url')

    if not youtube_url:
        return jsonify({"error": "No YouTube URL provided"}), 400

    try:
        logging.info(f"Downloading audio from: {youtube_url}")
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            title = info['title']
            file_name = f"api/downloads/{title}.mp3"
            logging.info(f"Download successful: {file_name}")
            return jsonify({"message": "Download successful", "file": file_name})
    except Exception as e:
        logging.error(f"Error downloading audio: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Serve the React app
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    file_name = request.json.get('file_name')

    if not file_name:
        return jsonify({"error": "No file name provided"}), 400

    headers = {
        'authorization': ASSEMBLY_AI_API_KEY,
        'content-type': 'application/json',
    }
    
    try:
        with open(file_name, 'rb') as audio_file:
            audio_data = audio_file.read()
    except FileNotFoundError:
        logging.error("File not found")
        return jsonify({"error": "File not found"}), 404

    response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, data=audio_data)
    
    if response.status_code != 200:
        logging.error("Upload failed: %s", response.text)
        return jsonify({"error": response.json().get("error", "Error uploading file")}), 500

    audio_url = response.json().get('upload_url')

    transcription_request = {
        'audio_url': audio_url,
        'language_detection': True,
        'language_confidence_threshold': 0.4,
    }

    response = requests.post('https://api.assemblyai.com/v2/transcript', json=transcription_request, headers=headers)
    
    if response.status_code != 200:
        logging.error("Transcription request failed: %s", response.text)
        return jsonify({"error": response.json().get("error", "Error creating transcription")}), 500

    transcript_id = response.json().get('id')
    return jsonify({"message": "Transcription request created", "transcript_id": transcript_id})

@app.route('/transcription_result/<transcript_id>', methods=['GET'])
def transcription_result(transcript_id):
    headers = {
        'authorization': ASSEMBLY_AI_API_KEY,
    }
    
    response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
    
    if response.status_code != 200:
        logging.error("Error fetching transcription result: %s", response.text)
        return jsonify({"error": response.json().get("error", "Error fetching transcription result")}), 500

    transcript_result = response.json()
    return jsonify(transcript_result)

if __name__ == '__main__':
    app.run(debug=True)
