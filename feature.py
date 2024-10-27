from flask import Flask, request, jsonify # type: ignore
import requests # type: ignore
import base64
import os

app = Flask(__name__)

# Configuration for ACRCloud
ACR_API_URL = "https://api.acrcloud.com/v1/identify"
ACR_API_KEY = "YOUR_ACR_CLOUD_API_KEY"  # Replace with your ACRCloud API key
ACR_API_SECRET = "YOUR_ACR_CLOUD_API_SECRET"  # Replace with your ACRCloud API secret

# Spotify API credentials
SPOTIFY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"  # Replace with your Spotify Client ID
SPOTIFY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"  # Replace with your Spotify Client Secret

def get_spotify_access_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}'.encode()).decode()}"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json().get('access_token')

def search_spotify(title, artist):
    token = get_spotify_access_token()
    query = f"{title} {artist}"
    url = f"https://api.spotify.com/v1/search?q={query}&type=track"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    results = response.json()
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        return track['external_urls']['spotify']
    return None

def search_youtube(title, artist):
    # You need to replace this with your own YouTube Data API implementation
    query = f"{title} {artist} music"
    return f"https://www.youtube.com/results?search_query={query}"

@app.route('/detect_music', methods=['POST'])
def detect_music():
    # Receive the video file
    file = request.files['video']
    file_path = f'temp_video.{file.filename.split(".")[-1]}'
    file.save(file_path)

    # Extract audio from video (using ffmpeg)
    audio_path = "temp_audio.wav"
    os.system(f"ffmpeg -i {file_path} -ac 1 -ar 16000 -y {audio_path}")

    # Call the music recognition API
    music_info = identify_music(audio_path)

    # Clean up temporary files
    os.remove(file_path)
    os.remove(audio_path)

    return jsonify(music_info)

def identify_music(audio_file):
    with open(audio_file, 'rb') as f:
        audio_data = f.read()

    # Encode audio data
    encoded_audio = base64.b64encode(audio_data).decode('utf-8')

    # Prepare the API request
    data = {
        "sample": {
            "data": encoded_audio,
            "format": "wav",
            "duration": int(os.path.getsize(audio_file) / (16000 * 2))  # Adjust according to audio format
        },
        "app": {
            "key": ACR_API_KEY,
            "secret": ACR_API_SECRET
        }
    }

    response = requests.post(ACR_API_URL, json=data)
    response_data = response.json()

    if response_data.get("status") == 0:
        # Music found
        music = response_data['metadata']['music'][0]
        title = music['title']
        artist = music['artists'][0]['name']

        # Search for music links
        spotify_link = search_spotify(title, artist)
        youtube_link = search_youtube(title, artist)

        return {
            "title": title,
            "artist": artist,
            "spotify": spotify_link,
            "youtube": youtube_link
        }
    else:
        return {"error": "Music not found."}

if __name__ == '__main__':
    # Make sure Tesseract is installed and correctly configured in your PATH
    app.run(debug=True)
