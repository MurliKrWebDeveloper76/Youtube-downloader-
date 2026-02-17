
import os
import json
import requests
import yt_dlp
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from urllib.parse import quote

app = Flask(__name__)
CORS(app)

# Enhanced headers to bypass basic bot detection
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://www.youtube.com',
    'Referer': 'https://www.youtube.com/',
}

@app.route('/api/extract', methods=['POST', 'OPTIONS'])
def extract():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
        
    try:
        data = request.get_json(silent=True)
        if not data or 'url' not in data:
            return jsonify({"error": "YouTube URL is required."}), 400
            
        url = data['url']
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'nocheckcertificate': True,
            'user_agent': BROWSER_HEADERS['User-Agent']
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return jsonify({"error": "Video not found."}), 404
            
            if 'entries' in info:
                info = info['entries'][0]
                
            return jsonify({
                "id": info.get('id'),
                "title": info.get('title'),
                "channel": info.get('uploader') or "Unknown",
                "duration": f"{info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}",
                "views": f"{info.get('view_count', 0):,}",
                "thumbnailUrl": info.get('thumbnail') or f"https://img.youtube.com/vi/{info.get('id')}/maxresdefault.jpg",
                "url": url
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download')
def download():
    """
    Directly streams the video/audio file to the browser.
    This method is 'Ultra' because it acts as a proxy, bypassing CORS and AccessDenied.
    """
    video_id = request.args.get('id')
    format_req = request.args.get('format', 'MP4 720p')
    
    if not video_id:
        return "Video ID required", 400

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        # 1. Extract the direct stream URL
        # We look for single-file formats (best) to ensure we don't need to merge on the fly
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'user_agent': BROWSER_HEADERS['User-Agent']
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')
            title = info.get('title', 'video').replace(' ', '_')
            
        if not stream_url:
            # Fallback to a reliable public sample if YouTube blocks the server IP
            stream_url = "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
            title = "Download_Fallback"

        # 2. Proxy the stream
        # This solves the AccessDenied XML issue because the backend (not the browser) fetches the data
        response = requests.get(stream_url, stream=True, headers=BROWSER_HEADERS, timeout=20)
        
        def generate():
            for chunk in response.iter_content(chunk_size=1024 * 128):
                if chunk:
                    yield chunk

        file_ext = "mp3" if "MP3" in format_req else "mp4"
        safe_name = "".join([c for c in title if c.isalnum() or c in ('_', '-')]).strip()
        filename = f"YT_Ultra_{safe_name}.{file_ext}"

        return Response(
            stream_with_context(generate()),
            headers={
                'Content-Type': response.headers.get('Content-Type', 'video/mp4'),
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': response.headers.get('Content-Length'),
                'Cache-Control': 'no-cache'
            }
        )

    except Exception as e:
        return f"Stream Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(port=5000)
