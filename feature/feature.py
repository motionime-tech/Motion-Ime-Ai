import requests
import response  # Mengimpor modul response.py
from pydub.utils 
import mediainfo

def get_audio_duration(file_path):
    # Menggunakan pydub untuk mendapatkan durasi file audio
    try:
        info = mediainfo(file_path)
        duration = float(info['duration'])  # Durasi dalam detik
        return duration
    except Exception as e:
        print(f"Error saat mendapatkan durasi file: {e}")
        return None

def find_song_from_audio(file_path, api_key):
    # Cek durasi file audio
    duration = get_audio_duration(file_path)
    
    if duration is None:
        print("Gagal memproses durasi file.")
        return
    
    # Jika durasi lebih dari 10 menit (600 detik), hentikan proses
    if duration > 600:
        print(f"Maaf Audio terlalu panjang! Durasi file lebih dari 10 menit ({duration / 60:.2f} menit).")
        return

def find_song_from_audio(file_path):
    # URL untuk mengirimkan request ke Audd.io
    url = "https://api.audd.io/"
    
    # Membaca file audio
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            
            # Parameter request
            data = {
                'api_token': api_key,
                'return': 'lyrics,track',
            }
            
            # Mengirim request
            response_api = requests.post(url, data=data, files=files)
            result = response_api.json()
            
            # Menangani hasil response dari Audd.io
            if result['status'] == 'success' and 'track' in result:
                track = result['track']
                print(f"Lagu ditemukan: {track['title']} oleh {track['artist']}")
                print(f"Link sumber di YouTube: {track['url']}")
                print(f"Link sumber di Spotify: {track['spotify_url']}")
                print(f"Link sumber di TikTok: {track['tiktok_url']}")
            else:
                # Jika lagu tidak ditemukan, kita panggil response.py untuk menangani ini
                response.handle_no_song_found()  # Menangani kasus lagu tidak ditemukan
                
    except requests.exceptions.RequestException as e:
        # Jika terjadi error pada permintaan HTTP
        print(f"Terjadi error saat menghubungi API Audd.io: {e}")
        response.log_error(f"Request failed: {e}")

    except FileNotFoundError:
        print(f"File tidak ditemukan: {file_path}")
        response.log_error(f"File not found: {file_path}")

# Ganti dengan API key dari Audd.io
api_key = 'your_api_key_here'

# Ganti dengan path file audio/video yang akan dianalisis
file_path = './audio_file.mp3'

# Panggil fungsi untuk mencari lagu
find_song_from_audio(file_path)
