api_token = 'PUT_YOUR_TOKEN_HERE'
url = 'https://api.audd.io/'

async def function_analyze_song(audio_file_path, webhook_url):
    """
    Analyze song with audd.io API

    Parameters:
        audio_file_path (str): Path location audio

    Returns:
        dict: Inform the detected song or return error if not found in database
    """
    # Capture message for realistic response
    message_id = send_webhook_debug("🌐 Communicating with AudD API... ⏳")

    # Required Parameter
    params = {
        'api_token': api_token,
        'return': 'apple_music,spotify,deezer',
        'market': 'us', #us is global
    }

    try:
        # Open Audio File with specify path
        with open(audio_file_path, 'rb') as audio_file:
            files = {'file': audio_file}
            response = requests.post(url, data=params, files=files)
            result = response.json()

        # Capture success from status
        if result.get('status') == 'success':
            song_info = {
                "title": result['result']['title'],
                "artist": result['result']['artist'],
                "platforms": {}
            }

            # Spotify
            if 'spotify' in result['result'] and result['result']['spotify']:
                spotify_data = result['result']['spotify']
                spotify_title = spotify_data.get('name', '')
                spotify_artist = ", ".join(
                    artist['name'] for artist in spotify_data.get('artists', [])
                )
                spotify_link = spotify_data.get('external_urls', {}).get('spotify', '')
                song_info['platforms']['spotify'] = {
                    "title": spotify_title,
                    "artist": spotify_artist,
                    "link": spotify_link,
                }

            # Capture Apple Music
            if 'apple_music' in result['result'] and result['result']['apple_music']:
                apple_music_data = result['result']['apple_music']
                apple_music_title = apple_music_data.get('name', '')
                apple_music_artist = apple_music_data.get('artistName', '')
                apple_music_link = apple_music_data.get('url', '')
                song_info['platforms']['apple_music'] = {
                    "title": apple_music_title,
                    "artist": apple_music_artist,
                    "link": apple_music_link,
                }

            # Capture Deezer
            if 'deezer' in result['result'] and result['result']['deezer']:
                deezer_data = result['result']['deezer']
                deezer_title = deezer_data.get('title', '')
                deezer_artist = deezer_data['artist'].get('name', '')
                deezer_link = deezer_data.get('link', '')
                song_info['platforms']['deezer'] = {
                    "title": deezer_title,
                    "artist": deezer_artist,
                    "link": deezer_link,
                }

            # Customize output msg
            output_message = f"Song Found!\n"
            titleori = result['result'].get('title', 'Unknown Title')
            artistori = result['result'].get('artist', 'Unknown Artist')
            # Show availabe platform
            for platform, data in song_info['platforms'].items():
                formatted_title = f"{data['title']} - {data['artist']}"
                output_message += f" - {platform.capitalize()}: [{formatted_title}]({data['link']})\n"

            # Edit msg to make sure plugin is finished
            if message_id:
                os.remove(audio_file_path)
                edit_message(
                    message_id,
                    new_description=f"Sound match as: {titleori} - {artistori}",
                    finish=True
                )
                await send_message_channel(
                    webhook_url,
                    None,
                    f"{output_message}",
                    "Motion Ime | Ai Playground",
                    None
                )
                return
            return song_info
        else:
            os.remove(audio_file_path)
            error_message = result.get('error', 'Song not found / request invalid')
            if message_id:
                edit_message(
                    message_id,
                    new_description=f"❌ Error: {error_message}",
                    finish=True
                )
            return {"error": error_message}

    except Exception as e:
        error_message = str(e)
        print(e)
        os.remove(audio_file_path)
        if message_id:
            edit_message(
                message_id,
                new_description=f"❌ Error: Anomaly Error",
                finish=True
            )
        return {"error": error_message}