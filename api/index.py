
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
        
        # Optimized yt-dlp configuration for serverless
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'extract_flat': False,
            'nocheckcertificate': True,
            'socket_timeout': 10,
            'no_color': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Attempt to extract metadata
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({"error": "Unable to find video information. The video might be private or restricted."}), 404

            # Handle playlists - take first entry
            if 'entries' in info:
                info = info['entries'][0]
            
            # Format outputs
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
        # Log error to Vercel console
        print(f"Server Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/download', methods=['GET'])
def download():
    video_id = request.args.get('id')
    format_type = request.args.get('format', 'mp4')
    return jsonify({
        "status": "Ready",
        "id": video_id,
        "format": format_type,
        "message": "Stream initialized. Vercel hobby limits apply (10s timeout)."
    })

# Root catch-all for health checks
@app.route('/api/', methods=['GET'])
def health():
    return jsonify({"status": "active", "engine": "yt-dlp"}), 200

if __name__ == "__main__":
    app.run(port=5000)
