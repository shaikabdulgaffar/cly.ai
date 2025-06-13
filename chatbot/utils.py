import requests
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup
import base64
import os
import re
import yt_dlp
import glob

def extract_youtube_id(url):
    """
    Extracts the YouTube video ID from a URL.
    """
    import re
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_youtube_transcript(url):
    try:
        video_id = extract_youtube_id(url)
        if not video_id:
            return None, "Invalid YouTube URL."
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            print("Available transcripts:", transcript_list)
            # Try to fetch English transcript
            try:
                transcript = transcript_list.find_transcript(['en'])
            except Exception as e:
                print("English transcript not found, trying manually created ones.")
                try:
                    transcript = transcript_list.find_manually_created_transcript(['en'])
                except Exception as e2:
                    print("No manually created English transcript, trying any transcript.")
                    # Try to get any transcript (first available)
                    try:
                        transcript = next(iter(transcript_list))
                    except Exception as e3:
                        print("No transcripts available at all.")
                        return None, "No transcripts available for this video."
            try:
                response = transcript.fetch()
            except Exception as fetch_exc:
                print("Transcript fetch failed:", fetch_exc)
                return None, f"Transcript fetch failed: {str(fetch_exc)}"
            print("Fetched transcript:", response)
            if not response or not isinstance(response, list):
                return None, "Transcript is empty or invalid."
            transcript_text = " ".join([t['text'] for t in response if 'text' in t])
            if not transcript_text.strip():
                return None, "Transcript is empty."
            return transcript_text, None
        except Exception as e:
            print("Transcript fetch exception:", e)
            return None, f"Transcript fetch error: {str(e)}"
    except Exception as e:
        print("General exception:", e)
        return None, f"Transcript fetch error: {str(e)}"

def summarize_with_gemini(transcript_text, gemini_api_key):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"Summarize this transcript: {transcript_text}"}]}]
    }
    params = {"key": gemini_api_key}
    resp = requests.post(url, json=payload, headers=headers, params=params)
    try:
        summary = resp.json()['candidates'][0]['content']['parts'][0]['text']
        return summary
    except Exception:
        return "Failed to summarize."

def get_lyrics_and_details(song_title, genius_token, gemini_api_key):
    # Step 1: Get song details from Spotify
    song_info = get_spotify_song_info(song_title)
    if not song_info:
        song_info = {"title": song_title, "artist": "", "album": "", "genre": "", "release_date": ""}

    # Step 2: Get lyrics from Genius
    search_url = "https://api.genius.com/search"
    headers = {"Authorization": f"Bearer {genius_token}"}
    params = {"q": song_title}
    resp = requests.get(search_url, params=params, headers=headers)
    data = resp.json()
    if not data['response']['hits']:
        return None, None, "Song not found."
    song = data['response']['hits'][0]['result']
    # Update title/artist if missing from Spotify
    if not song_info.get("title"):
        song_info["title"] = song['title']
    if not song_info.get("artist"):
        song_info["artist"] = song['primary_artist']['name']

    # Scrape lyrics from the Genius page
    song_page = requests.get(song['url'])
    html = BeautifulSoup(song_page.text, "html.parser")
    lyrics_divs = html.find_all("div", {"data-lyrics-container": "true"})
    if lyrics_divs:
        lyrics = "\n".join(div.get_text(separator='\n') for div in lyrics_divs)
    else:
        lyrics_div = html.find("div", class_="lyrics")
        if lyrics_div:
            lyrics = lyrics_div.get_text(separator='\n')
        else:
            lyrics = "Lyrics not found."

    # Step 3: Clean lyrics
    cleaned_lyrics = clean_lyrics_text(lyrics)
    formatted_lyrics = format_lyrics_sections(cleaned_lyrics)

    # Step 4: Merge details and lyrics (no Gemini needed for cleaning)
    enhanced_lyrics = f"""
<b style="font-size:1.5em;">{song_info.get('title','')}</b><br>
<br>
Song Artist: {song_info.get('artist','')}<br>
Album/Movie: {song_info.get('album','')}<br>
Genre: {song_info.get('genre','')}<br>
Release Date: {song_info.get('release_date','')}<br>
<br>
{formatted_lyrics}
"""
    return enhanced_lyrics, song_info, None

def chat_with_gemini(prompt, gemini_api_key):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    params = {"key": gemini_api_key}
    resp = requests.post(url, json=payload, headers=headers, params=params)
    print("Gemini API key:", gemini_api_key)
    print("Prompt:", prompt)
    print("Gemini status:", resp.status_code)
    print("Gemini response:", resp.text)
    try:
        return resp.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print("Gemini exception:", e)
        return "Sorry, I couldn't process your request."

def get_spotify_song_info(song_title):
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        return {}

    # Get access token
    auth_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}"}
    data = {"grant_type": "client_credentials"}
    resp = requests.post(auth_url, headers=headers, data=data)
    access_token = resp.json().get("access_token")
    if not access_token:
        return {}

    # Search song
    search_url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"q": song_title, "type": "track", "limit": 1}
    resp = requests.get(search_url, headers=headers, params=params)
    items = resp.json().get("tracks", {}).get("items", [])
    if not items:
        return {}

    track = items[0]
    album = track["album"]
    artist_id = track["artists"][0]["id"]

    # Fetch genre from artist endpoint
    artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
    artist_resp = requests.get(artist_url, headers=headers)
    genres = artist_resp.json().get("genres", [])
    genre_str = ", ".join(genres) if genres else ""

    return {
        "album": album["name"],
        "release_date": album.get("release_date"),
        "spotify_url": track["external_urls"]["spotify"],
        "album_image": album["images"][0]["url"] if album["images"] else "",
        "artist": track["artists"][0]["name"],
        "genre": genre_str,
    }

def clean_lyrics_text(lyrics):
    """
    Remove contributors, translations, descriptions, credits, language names, and extra info from lyrics.
    Only keep section headers ([...]) and actual lyrics lines.
    """
    import unicodedata

    unwanted_keywords = [
        "contributors", "translations", "read more", "lyrics", "released", "see", "embed",
        "copyright", "you might also like", "about", "album", "tracklist", "credits", "produced by",
        "written by", "composed by", "mix", "master", "engineer", "label", "publisher", "recorded",
        "release date", "view all", "expand", "genius", "remix", "feat.", "featuring"
    ]

    def strip_accents(text):
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

    def is_language_line(line):
        # Remove lines that are mostly non-ASCII (like Ελληνικά, العربية, 한국어)
        non_ascii = sum(1 for c in line if ord(c) > 127)
        if non_ascii > 0 and len(line.split()) <= 3:
            return True
        # Remove lines that are short and only contain letters/spaces/punctuation, but not section headers
        if re.match(r'^[\W\w\s\(\)\-\.\']+$', line) and len(line.split()) <= 3 and not re.match(r'^\[.*\]$', line):
            return True
        return False

    lines = lyrics.split('\n')
    cleaned = []
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        line_lower = strip_accents(line_stripped.lower())
        # Remove lines with unwanted keywords
        if any(keyword in line_lower for keyword in unwanted_keywords):
            continue
        # Remove language lines and short non-lyrics lines (but keep section headers)
        if is_language_line(line_stripped):
            continue
        # Remove lines that are just numbers
        if re.match(r'^\d+$', line_stripped):
            continue
        # Remove lines that are just section dividers
        if re.match(r'^[-–—\s]+$', line_stripped):
            continue
        cleaned.append(line_stripped)
    return '\n'.join(cleaned)

def format_lyrics_sections(lyrics):
    # Add <br> before and after each section header like [Chorus], [Verse 1], etc.
    formatted = re.sub(r'(\[[^\]]+\])', r'<br>\1<br>', lyrics)
    return formatted.replace('\n', '<br>')

def get_youtube_subtitle_transcript(youtube_url, lang='en'):
    try:
        # Get video ID
        video_id = extract_youtube_id(youtube_url)
        if not video_id:
            return None, "Invalid YouTube URL."
        # Download subtitles
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [lang],
            'skip_download': True,
            'outtmpl': '%(id)s.%(ext)s',
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
            vtt_files = glob.glob(f"{video_id}*.vtt")
            if not vtt_files:
                return None, "No subtitles found for this language."
            vtt_filename = vtt_files[0]
            # Clean text
            lines = []
            with open(vtt_filename, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("WEBVTT") or "-->" in line or line.startswith("Kind:") or line.startswith("Language:"):
                        continue
                    line = re.sub(r'<.*?>', '', line)
                    if line:
                        lines.append(line)
            os.remove(vtt_filename)
            # Remove duplicates
            cleaned = []
            for i, l in enumerate(lines):
                if i == 0 or l != lines[i-1]:
                    cleaned.append(l)
            transcript = "\n".join(cleaned)
            if not transcript.strip():
                return None, "Transcript is empty."
            return transcript, None
    except Exception as e:
        return None, f"Subtitle fetch error: {str(e)}"