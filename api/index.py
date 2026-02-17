import os
import requests
import yt_dlp
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

@app.route('/api/video_info', methods=['POST', 'OPTIONS'])
def video_info():
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
            'nocheckcertificate': True,
            'noplaylist': True,
            'user_agent': BROWSER_HEADERS['User-Agent'],
            'socket_timeout': 5,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return jsonify({"error": "Video not found."}), 404
            
            # Extract basic info
            metadata = {
                "id": info.get('id'),
                "title": info.get('title'),
                "author": info.get('uploader') or info.get('channel', 'Unknown'),
                "duration": f"{info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}",
                "views": f"{info.get('view_count', 0):,}",
                "description": info.get('description', '')[:200] + '...',
                "thumbnailUrl": info.get('thumbnail'),
                "publish_date": info.get('upload_date', 'Unknown'),
                "url": url
            }
            
            return jsonify(metadata)
            
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
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # Filter for common progressive mp4 resolutions
            res_set = set()
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    res = f.get('resolution') or f"{f.get('height')}p"
                    if 'p' in str(res):
                        res_set.add(str(res))
            
            return jsonify({
                "progressive": sorted(list(res_set), key=lambda x: int(x.replace('p', '')) if x.replace('p', '').isdigit() else 0),
                "audio": ["128kbps", "192kbps", "320kbps"]
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download')
def download():
    video_id = request.args.get('id')
    res_req = request.args.get('resolution', 'best')
    format_type = request.args.get('type', 'mp4') # mp4 or mp3
    
    if not video_id:
        return "Video ID required", 400

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        # Configuration for streaming
        ydl_opts = {
            'format': f'bestvideo[height<={res_req[:-1]}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if format_type == 'mp4' else 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'user_agent': BROWSER_HEADERS['User-Agent'],
            'socket_timeout': 10,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')
            title = info.get('title', 'video').replace(' ', '_')
            
        if not stream_url:
            raise Exception("Stream URL not found")

        resp = requests.get(stream_url, stream=True, headers=BROWSER_HEADERS, timeout=10)
        resp.raise_for_status()

        def stream_content():
            for chunk in resp.iter_content(chunk_size=524288): # 512KB chunks
                if chunk:
                    yield chunk

        safe_title = "".join([c for c in title if c.isalnum() or c in ('-', '_')])[:50]
        filename = f"YT_Ultra_{safe_title}.{format_type}"

        # FORCED DOWNLOAD HEADERS
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Transfer-Encoding': 'binary',
            'X-Content-Type-Options': 'nosniff',
            'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
            'Pragma': 'no-cache',
            'Expires': '0',
        }
        
        if resp.headers.get('Content-Length'):
            headers['Content-Length'] = resp.headers.get('Content-Length')

        return Response(stream_with_context(stream_content()), headers=headers)

    except Exception as e:
        return f"Download server error: {str(e)}", 500

if __name__ == "__main__":
    app.run(port=5000)
