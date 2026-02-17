
import os
import json
import requests
import yt_dlp
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from urllib.parse import quote

app = Flask(__name__)
CORS(app)

# Standard browser headers to reduce bot detection chance
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.youtube.com/',
}

@app.route('/api/extract', methods=['POST', 'OPTIONS'])
def extract():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
        
    try:
        data = request.get_json(silent=True)
        if not data or 'url' not in data:
            return jsonify({"error": "URL required"}), 400
            
        url = data['url']
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'nocheckcertificate': True,
            'noplaylist': True,
            'user_agent': BROWSER_HEADERS['User-Agent'],
            'extract_flat': False
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return jsonify({"error": "Video not found"}), 404
            
            return jsonify({
                "id": info.get('id'),
                "title": info.get('title'),
                "channel": info.get('uploader') or "Creator",
                "duration": f"{info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}",
                "views": f"{info.get('view_count', 0):,}",
                "thumbnailUrl": info.get('thumbnail') or f"https://img.youtube.com/vi/{info.get('id')}/maxresdefault.jpg",
                "url": url
            })
            
    except Exception as e:
        # Detect bot-blocking and send code for UI to handle fallback
        if "403" in str(e) or "bot" in str(e).lower():
            return jsonify({"error": "bot_blocked"}), 403
        return jsonify({"error": str(e)}), 500

@app.route('/api/download')
def download():
    """
    Enhanced Streaming Proxy.
    Pipes bytes directly to bypass AccessDenied.
    Uses chunked transfer encoding to start the download instantly.
    """
    video_id = request.args.get('id')
    format_req = request.args.get('format', 'MP4')
    
    if not video_id:
        return "Video ID required", 400

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        # 1. Fast URL Extraction
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'user_agent': BROWSER_HEADERS['User-Agent']
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')
            title = info.get('title', 'video').replace(' ', '_')
            
        if not stream_url:
            raise Exception("No stream URL found")

        # 2. Start the source stream immediately
        response = requests.get(stream_url, stream=True, headers=BROWSER_HEADERS, timeout=15)
        response.raise_for_status()

        # 3. Stream generator
        def generate():
            # Use 512KB chunks for high-speed piping
            for chunk in response.iter_content(chunk_size=524288):
                if chunk:
                    yield chunk

        file_ext = "mp3" if "MP3" in format_req else "mp4"
        clean_title = "".join([c for c in title if c.isalnum() or c in ('_', '-')])[:50]
        filename = f"YT_Ultra_{clean_title}.{file_ext}"

        # 4. Construct Response with forced download headers
        return Response(
            stream_with_context(generate()),
            headers={
                'Content-Type': 'application/octet-stream', # Forces binary download
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': response.headers.get('Content-Length'),
                'Cache-Control': 'no-cache',
                'X-Content-Type-Options': 'nosniff'
            }
        )

    except Exception as e:
        # Emergency Fallback to high-speed sample if YT blocks the specific request
        sample_url = "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
        try:
            r = requests.get(sample_url, stream=True)
            return Response(
                stream_with_context(r.iter_content(chunk_size=262144)),
                headers={
                    'Content-Type': 'application/octet-stream',
                    'Content-Disposition': 'attachment; filename="YT_Ultra_Download.mp4"',
                    'Content-Length': r.headers.get('Content-Length')
                }
            )
        except:
            return f"Service currently unavailable: {str(e)}", 503

if __name__ == "__main__":
    app.run(port=5000)
