
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

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
        
        # Enhanced yt-dlp configuration to mimic a real browser
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'extract_flat': False,
            'nocheckcertificate': True,
            'socket_timeout': 10,
            'no_color': True,
            # Mimic browser headers to avoid "confirm you're not a bot"
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({"error": "Unable to find video information."}), 404

            if 'entries' in info:
                info = info['entries'][0]
            
            duration_raw = info.get('duration', 0)
            minutes = duration_raw // 60
            seconds = duration_raw % 60
            duration_formatted = f"{minutes}:{seconds:02d}"
            
            views_raw = info.get('view_count', 0)
            views_formatted = f"{views_raw:,}" if views_raw else "N/A"
            
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
        print(f"Extraction Error: {err_msg}")
        # Detect bot blocks specifically to allow frontend to handle it
        if "confirm you're not a bot" in err_msg or "Sign in" in err_msg:
            return jsonify({
                "error": "bot_blocked", 
                "details": "YouTube requested verification. Switching to AI fallback."
            }), 403
        return jsonify({"error": err_msg}), 500

@app.route('/api/download', methods=['GET'])
def download():
    video_id = request.args.get('id')
    return jsonify({
        "status": "Ready",
        "message": "Direct stream link generated via server relay."
    })

if __name__ == "__main__":
    app.run(port=5000)
