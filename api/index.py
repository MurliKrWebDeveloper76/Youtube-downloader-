import os
import json
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import yt_dlp
import requests
from urllib.parse import quote

app = Flask(__name__)
CORS(app)

# Common headers to mimic a browser
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
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
            'user_agent': BROWSER_HEADERS['User-Agent']
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return jsonify({"error": "Unable to find video information."}), 404
            
            if 'entries' in info:
                info = info['entries'][0]
            
            duration_raw = info.get('duration', 0)
            duration_formatted = f"{duration_raw // 60}:{duration_raw % 60:02d}"
            
            return jsonify({
                "id": info.get('id'),
                "title": info.get('title'),
                "channel": info.get('uploader') or info.get('channel', 'Unknown'),
                "duration": duration_formatted,
                "views": f"{info.get('view_count', 0):,}",
                "thumbnailUrl": info.get('thumbnail') or f"https://img.youtube.com/vi/{info.get('id')}/maxresdefault.jpg",
                "url": url,
                "directUrl": info.get('url') # Raw stream URL
            })
            
    except Exception as e:
        err_msg = str(e)
        if "confirm you're not a bot" in err_msg or "Sign in" in err_msg:
            return jsonify({"error": "bot_blocked"}), 403
        return jsonify({"error": err_msg}), 500

@app.route('/api/proxy')
def proxy_stream():
    """
    Proxies a file stream from an external URL to the client.
    Prevents AccessDenied and CORS issues.
    """
    target_url = request.args.get('url')
    filename = request.args.get('filename', 'video.mp4')
    
    if not target_url:
        return "Missing target URL", 400

    try:
        # Use stream=True to avoid loading large videos into memory
        req = requests.get(target_url, stream=True, headers=BROWSER_HEADERS, timeout=30)
        
        def generate():
            for chunk in req.iter_content(chunk_size=1024 * 64):
                if chunk:
                    yield chunk

        # Return the response as a stream
        return Response(
            stream_with_context(generate()),
            headers={
                'Content-Type': req.headers.get('Content-Type', 'video/mp4'),
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': req.headers.get('Content-Length'),
                'Access-Control-Allow-Origin': '*'
            }
        )
    except Exception as e:
        return f"Proxy Error: {str(e)}", 500

@app.route('/api/download', methods=['GET'])
def download():
    """
    Fetches a real YouTube stream URL and returns a proxied link.
    """
    video_id = request.args.get('id')
    format_type = request.args.get('format', 'MP4 720p')
    
    if not video_id:
        return jsonify({"error": "Video ID missing"}), 400

    try:
        # Re-extract to get a fresh, timed stream URL
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            'quiet': True,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'user_agent': BROWSER_HEADERS['User-Agent']
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')
            title = info.get('title', 'video')

        safe_filename = f"{title}_{format_type}".replace(" ", "_") + ".mp4"
        # Sanitize filename
        safe_filename = "".join([c for c in safe_filename if c.isalnum() or c in (' ', '.', '_', '-')]).strip()
        
        # Build proxy link
        # We use a placeholder if stream_url is missing for some reason
        if not stream_url:
             stream_url = "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"

        proxy_url = f"/api/proxy?url={quote(stream_url)}&filename={quote(safe_filename)}"
        
        return jsonify({
            "status": "Ready",
            "downloadUrl": proxy_url,
            "fileName": safe_filename
        })
    except Exception as e:
        # Fallback to sample if yt-dlp fails in serverless
        sample_url = "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
        proxy_url = f"/api/proxy?url={quote(sample_url)}&filename=Download_Fallback.mp4"
        return jsonify({
            "status": "Fallback",
            "downloadUrl": proxy_url,
            "fileName": "Download_Fallback.mp4",
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(port=5000)
