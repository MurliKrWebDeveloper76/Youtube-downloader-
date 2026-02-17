
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
            return jsonify({"error": "Invalid JSON or missing body"}), 400
            
        url = data.get('url')
        if not url:
            return jsonify({"error": "No URL provided"}), 400
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'extract_flat': False,
            'nocheckcertificate': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
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
                "thumbnailUrl": info.get('thumbnail'),
                "url": url
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This allows the file to be run as a standalone Flask app for local testing
if __name__ == "__main__":
    app.run(port=5000)
