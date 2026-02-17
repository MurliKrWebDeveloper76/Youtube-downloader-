
import os
import json
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

# Common headers to mimic a browser
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Fetch-Mode': 'navigate',
}

@app.route('/api/extract', methods=['POST', 'OPTIONS'])
def extract():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
        
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid request. JSON body missing."}), 400
            
        url = data.get('url')
        if not url:
            return jsonify({"error": "YouTube URL is required."}), 400
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'extract_flat': False,
            'nocheckcertificate': True,
            'socket_timeout': 10,
            'user_agent': BROWSER_HEADERS['User-Agent'],
            'http_headers': BROWSER_HEADERS
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return jsonify({"error": "Unable to find video information."}), 404
            if 'entries' in info:
                info = info['entries'][0]
            
            duration_raw = info.get('duration', 0)
            duration_formatted = f"{duration_raw // 60}:{duration_raw % 60:02d}"
            views_formatted = f"{info.get('view_count', 0):,}"
            
            return jsonify({
                "id": info.get('id'),
                "title": info.get('title'),
                "channel": info.get('uploader') or info.get('channel', 'Unknown'),
                "duration": duration_formatted,
                "views": views_formatted,
                "thumbnailUrl": info.get('thumbnail') or f"https://img.youtube.com/vi/{info.get('id')}/maxresdefault.jpg",
                "url": url
            })
            
    except Exception as e:
        err_msg = str(e)
        if "confirm you're not a bot" in err_msg or "Sign in" in err_msg:
            return jsonify({"error": "bot_blocked"}), 403
        return jsonify({"error": err_msg}), 500

@app.route('/api/download', methods=['GET'])
def download():
    """
    Returns a JSON payload with a download link. 
    In a production app, this would generate a signed URL or a proxy stream.
    """
    video_id = request.args.get('id', 'dQw4w9WgXcQ')
    format_type = request.args.get('format', 'MP4 720p')
    
    # We provide a publicly accessible video sample for the demo download.
    # In reality, this would be a dynamic stream from yt-dlp.
    return jsonify({
        "status": "Ready",
        "downloadUrl": "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "fileName": f"YT_Ultra_{video_id}_{format_type.replace(' ', '_')}.mp4"
    })

if __name__ == "__main__":
    app.run(port=5000)
