from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
from yt_dlp import YoutubeDL


load_dotenv()

app = Flask(__name__, static_folder='../frontend/build')
CORS(app)

# Set up yt-dlp options
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'noplaylist': True,
}

if not os.path.exists('downloads'):
    os.makedirs('downloads')

# Fetch the API key from environment variables
ASSEMBLY_AI_API_KEY = os.getenv('ASSEMBLY_AI_API_KEY')

@app.route('/download', methods=['POST'])
def download_audio():
    youtube_url = request.json.get('youtube_url')

    if not youtube_url:
        return jsonify({"error": "No YouTube URL provided"}), 400

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            title = info['title']
            file_name = f"downloads/{title}.mp3"
            return jsonify({"message": "Download successful", "file": file_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve the React app
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    file_name = request.json.get('file_name')

    if not file_name:
        return jsonify({"error": "No file name provided"}), 400

    # Upload the audio file to AssemblyAI
    headers = {
        'authorization': ASSEMBLY_AI_API_KEY,
        'content-type': 'application/json',
    }
    
    # Open and read the audio file
    try:
        with open(file_name, 'rb') as audio_file:
            audio_data = audio_file.read()
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

    # Uploading the audio file
    response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, data=audio_data)
    
    if response.status_code != 200:
        # Log the raw response for debugging
        print("Upload failed:", response.status_code, response.text)
        return jsonify({"error": response.json().get("error", "Error uploading file")}), 500

    audio_url = response.json().get('upload_url')

    # Set up transcription request with language detection enabled
    transcription_request = {
        'audio_url': audio_url,
        'language_detection': True,  # Enable automatic language detection
        'language_confidence_threshold': 0.4  # Set a threshold for language confidence
    }

    # Send the transcription request
    response = requests.post('https://api.assemblyai.com/v2/transcript', json=transcription_request, headers=headers)
    
    if response.status_code != 200:
        # Log the raw response for debugging
        print("Transcription request failed:", response.status_code, response.text)
        return jsonify({"error": response.json().get("error", "Error creating transcription")}), 500

    transcript_id = response.json().get('id')

    return jsonify({"message": "Transcription request created", "transcript_id": transcript_id})

@app.route('/transcription_result/<transcript_id>', methods=['GET'])
def transcription_result(transcript_id):
    # Fetch the transcription result from AssemblyAI
    headers = {
        'authorization': ASSEMBLY_AI_API_KEY,
    }
    
    response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
    
    if response.status_code != 200:
        return jsonify({"error": response.json().get("error", "Error fetching transcription result")}), 500

    transcript_result = response.json()
    
    return jsonify(transcript_result)
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
