import os
import subprocess
import json
import requests
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Standard browser headers to mimic a real user session
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def get_yt_dlp_binary():
    # Attempt to find yt-dlp binary
    return "yt-dlp"

@app.route('/api/video_info', methods=['POST', 'OPTIONS'])
def video_info():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
        
    try:
        data = request.get_json(silent=True)
        if not data or 'url' not in data:
            return jsonify({"error": "YouTube URL is required."}), 400
            
        url = data['url']
        cmd = [
            get_yt_dlp_binary(),
            '--quiet',
            '--no-warnings',
            '--nocheckcertificate',
            '--dump-json',
            '--no-playlist',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"error": "Could not extract video info. Video might be restricted or blocked."}), 400
            
        info = json.loads(result.stdout)
        
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
            
        cmd = [
            get_yt_dlp_binary(),
            '--quiet',
            '--dump-json',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)
        formats = info.get('formats', [])
        
        # We look for progressive formats (video + audio in one file) 
        # because Vercel doesn't have ffmpeg to merge separate streams.
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
    Streams binary data directly from yt-dlp stdout to the response.
    Forces application/octet-stream to prevent browser media players from hijacking.
    """
    video_id = request.args.get('id')
    res_req = request.args.get('resolution', '720p')
    format_type = request.args.get('type', 'mp4')
    
    if not video_id:
        return "Video ID required", 400

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    height = res_req.replace('p', '')
    
    # Select best progressive mp4 up to requested height
    # If mp3, select best audio
    if format_type == 'mp3':
        format_spec = 'bestaudio/best'
    else:
        format_spec = f'best[height<={height}][ext=mp4]/best'

    def generate():
        cmd = [
            get_yt_dlp_binary(),
            '-f', format_spec,
            '--no-playlist',
            '--no-warnings',
            '--nocheckcertificate',
            '-o', '-',  # Output to stdout
            video_url
        ]
        
        # Use Popen to pipe stdout directly
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        try:
            while True:
                chunk = proc.stdout.read(1024 * 512) # 512KB chunks
                if not chunk:
                    break
                yield chunk
        finally:
            proc.terminate()

    # Get title for filename
    try:
        title_cmd = [get_yt_dlp_binary(), '--get-title', '--no-playlist', video_url]
        title = subprocess.check_output(title_cmd).decode('utf-8').strip()
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
