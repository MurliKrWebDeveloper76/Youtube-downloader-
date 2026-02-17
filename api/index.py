import os
import sys
import subprocess
import json
import requests
import yt_dlp
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Absolute path to cookies.txt for reliable access in the Vercel environment
COOKIES_PATH = os.path.join(os.path.dirname(__file__), 'cookies.txt')

# Standard browser headers to mimic a real user session
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

@app.route('/api/video_info', methods=['POST', 'OPTIONS'])
def video_info():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
        
    try:
        data = request.get_json(silent=True)
        if not data or 'url' not in data:
            return jsonify({"error": "YouTube URL is required."}), 400
            
        url = data['url']
        
        # Use the library directly for info extraction
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'user_agent': BROWSER_HEADERS['User-Agent'],
            'cookiefile': COOKIES_PATH, # Engage cookies to bypass bot detection
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return jsonify({"error": "Video not found."}), 404
            
            return jsonify({
                "id": info.get('id'),
                "title": info.get('title'),
                "author": info.get('uploader') or info.get('channel', 'Unknown'),
                "duration": f"{info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}",
                "views": f"{info.get('view_count', 0):,}",
                "thumbnailUrl": info.get('thumbnail'),
                "url": url
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/available_resolutions', methods=['POST'])
def available_resolutions():
    try:
        data = request.get_json(silent=True)
        url = data.get('url')
        if not url:
            return jsonify({"error": "URL required"}), 400
            
        ydl_opts = {
            'quiet': True,
            'nocheckcertificate': True,
            'user_agent': BROWSER_HEADERS['User-Agent'],
            'cookiefile': COOKIES_PATH,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            res_set = set()
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    res = f.get('height')
                    if res:
                        res_set.add(f"{res}p")
            
            return jsonify({
                "progressive": sorted(list(res_set), key=lambda x: int(x.replace('p', ''))),
                "audio": ["128kbps", "192kbps", "320kbps"]
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download')
def download():
    """
    ULTRA DIRECT PIPE:
    Streams binary data directly from stdout to the response using cookies for session persistence.
    """
    video_id = request.args.get('id')
    res_req = request.args.get('resolution', '720p')
    format_type = request.args.get('type', 'mp4')
    
    if not video_id:
        return "Video ID required", 400

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    height = res_req.replace('p', '')
    
    if format_type == 'mp3':
        format_spec = 'bestaudio/best'
    else:
        format_spec = f'best[height<={height}][ext=mp4]/best'

    def generate():
        cmd = [
            sys.executable, "-m", "yt_dlp",
            '-f', format_spec,
            '--no-playlist',
            '--no-warnings',
            '--nocheckcertificate',
            '--user-agent', BROWSER_HEADERS['User-Agent'],
            '--cookies', COOKIES_PATH, # Added cookies flag
            '-o', '-',  
            video_url
        ]
        
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        
        try:
            while True:
                chunk = proc.stdout.read(1024 * 512) 
                if not chunk:
                    break
                yield chunk
        finally:
            proc.terminate()

    try:
        ydl_opts = {'quiet': True, 'cookiefile': COOKIES_PATH}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'video')
    except:
        title = "video"

    safe_title = "".join([c for c in title if c.isalnum() or c in ('-', '_')])[:50]
    filename = f"YT_Ultra_{safe_title}.{format_type}"

    headers = {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': f'attachment; filename="{filename}"',
        'X-Content-Type-Options': 'nosniff',
        'Cache-Control': 'no-cache',
    }

    return Response(stream_with_context(generate()), headers=headers)

if __name__ == "__main__":
    app.run(port=5000)
