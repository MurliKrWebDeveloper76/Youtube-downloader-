
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# Allow CORS for development and production
CORS(app)

@app.route('/api/extract', methods=['POST'])
def extract():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "No URL provided"}), 400
        
        # Configure yt-dlp to extract info without downloading
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info
            info = ydl.extract_info(url, download=False)
            
            # Helper to format duration
            duration_raw = info.get('duration', 0)
            minutes = duration_raw // 60
            seconds = duration_raw % 60
            duration_formatted = f"{minutes}:{seconds:02d}"
            
            # Format view count with commas
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
        print(f"Error extracting metadata: {str(e)}")
        return jsonify({"error": "Failed to process the provided URL. Make sure it's a valid public YouTube video."}), 500

@app.route('/api/download', methods=['GET'])
def download():
    # In a production environment with Vercel Hobby, direct streaming might time out (10s limit).
    # This endpoint serves as a placeholder for the download logic.
    video_id = request.args.get('id')
    return jsonify({
        "status": "Ready",
        "message": "Stream initialized for " + str(video_id),
        "disclaimer": "Serverless functions have size limits. Use a dedicated worker for 100MB+ files."
    })

# Main entry point for local development
if __name__ == "__main__":
    app.run(port=5000)
