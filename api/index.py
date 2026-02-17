import os
import requests
import yt_dlp
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Standard browser headers to mimic a real user session and minimize blocks
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
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
            'noplaylist': True,
            'extract_flat': True, 
            'user_agent': BROWSER_HEADERS['User-Agent'],
            'socket_timeout': 5,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return jsonify({"error": "Video not found."}), 404
            
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
        error_msg = str(e)
        if "403" in error_msg:
            return jsonify({"error": "bot_blocked"}), 403
        return jsonify({"error": error_msg}), 500

@app.route('/api/download')
def download():
    """
    Direct-pipe binary stream handler.
    Strictly uses application/octet-stream and Content-Disposition attachment
    to force browser file downloads and prevent broken video player views.
    """
    video_id = request.args.get('id')
    format_req = request.args.get('format', 'MP4')
    
    if not video_id:
        return "Video ID required", 400

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        # Optimized for stream extraction speed
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'user_agent': BROWSER_HEADERS['User-Agent'],
            'socket_timeout': 10,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')
            title = info.get('title', 'video').replace(' ', '_')
            
        if not stream_url:
            raise Exception("Stream URL extraction failed")

        # Proxy the binary data from YouTube
        resp = requests.get(stream_url, stream=True, headers=BROWSER_HEADERS, timeout=10)
        resp.raise_for_status()

        def stream_content():
            # Use 512KB chunks for steady delivery
            for chunk in resp.iter_content(chunk_size=524288):
                if chunk:
                    yield chunk

        file_ext = "mp3" if "MP3" in format_req else "mp4"
        safe_title = "".join([c for c in title if c.isalnum() or c in ('-', '_')])[:50]
        filename = f"YT_Ultra_{safe_title}.{file_ext}"

        # Hardened headers to bypass browser players
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Transfer-Encoding': 'binary',
            'X-Content-Type-Options': 'nosniff',
            'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
            'Pragma': 'no-cache',
            'Expires': '0',
        }
        
        content_len = resp.headers.get('Content-Length')
        if content_len:
            headers['Content-Length'] = content_len

        return Response(stream_with_context(stream_content()), headers=headers)

    except Exception as e:
        return f"Download server encountered an error: {str(e)}", 500

if __name__ == "__main__":
    app.run(port=5000)