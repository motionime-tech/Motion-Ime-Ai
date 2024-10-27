from flask import Flask, request, jsonify
import requests
import base64
import os
import logging

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Configuration for ACRCloud
ACR_API_URL = "https://api.acrcloud.com/v1/identify"
ACR_API_KEY = "YOUR_ACR_CLOUD_API_KEY"  # Replace with your ACRCloud API key
ACR_API_SECRET = "YOUR_ACR_CLOUD_API_SECRET"  # Replace with your ACRCloud API secret

# Spotify API credentials
SPOTIFY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"  # Replace with your Spotify Client ID
SPOTIFY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"  # Replace with your Spotify Client Secret

# Last.fm API credentials
LASTFM_API_KEY = "YOUR_LASTFM_API_KEY"  # Replace with your Last.fm API key

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
    query = f"{title} {artist} music"
    youtube_api_key = "YOUR_YOUTUBE_API_KEY"  # Replace with your YouTube API key
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={youtube_api_key}&maxResults=1"
    response = requests.get(url)
    results = response.json()
    if results['items']:
        video_id = results['items'][0]['id']['videoId']
        return f"https://www.youtube.com/watch?v={video_id}"
    return None

def search_lastfm(title, artist):
    url = f"http://ws.audioscrobbler.com/2.0/?method=track.getinfo&api_key={LASTFM_API_KEY}&artist={artist}&track={title}&format=json"
    response = requests.get(url)
    data = response.json()
    if 'track' in data:
        track = data['track']
        return {
            "listeners": track.get('listeners'),
            "playcount": track.get('playcount'),
            "wiki": track.get('wiki', {}).get('summary'),
            "similar": [similar['name'] for similar in track.get('similar', {}).get('track', [])]
        }
    return None

@app.route('/detect_music', methods=['POST'])
def detect_music():
    file = request.files['video']
    file_path = f'temp_video.{file.filename.split(".")[-1]}'
    file.save(file_path)

    audio_path = "temp_audio.wav"
    os.system(f"ffmpeg -i {file_path} -ac 1 -ar 16000 -y {audio_path}")

    music_info = identify_music(audio_path)

    os.remove(file_path)
    os.remove(audio_path)

    return jsonify(music_info)

def identify_music(audio_file):
    with open(audio_file, 'rb') as f:
        audio_data = f.read()

    encoded_audio = base64.b64encode(audio_data).decode('utf-8')

    data = {
        "sample": {
            "data": encoded_audio,
            "format": "wav",
            "duration": int(os.path.getsize(audio_file) / (16000 * 2))
        },
        "app": {
            "key": ACR_API_KEY,
            "secret": ACR_API_SECRET
        }
    }

    response = requests.post(ACR_API_URL, json=data)
    response_data = response.json()

    if response_data.get("status") == 0:
        music = response_data['metadata']['music'][0]
        title = music['title']
        artist = music['artists'][0]['name']

        spotify_link = search_spotify(title, artist)
        youtube_link = search_youtube(title, artist)
        lastfm_info = search_lastfm(title, artist)

        return {
            "title": title,
            "artist": artist,
            "spotify": spotify_link,
            "youtube": youtube_link,
            "lastfm": lastfm_info
        }
    else:
        return {"error": "Music not found."}

if __name__ == '__main__':
    app.run(debug=True)
