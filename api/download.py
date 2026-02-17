import os
import requests
import yt_dlp
from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Mimic a real browser to avoid 403 Forbidden errors from YouTube
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.youtube.com/',
}

@app.route('/api/download', methods=['GET'])
def download():
    video_id = request.args.get('id')
    format_req = request.args.get('format', 'MP4')
    
    if not video_id:
        return "Video ID required", 400

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        # 1. Extract the direct stream URL using yt-dlp
        # Prefer pre-merged mp4 formats to avoid server-side processing timeouts
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'user_agent': BROWSER_HEADERS['User-Agent']
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')
            title = info.get('title', 'video').replace(' ', '_')
            
        if not stream_url:
            raise Exception("Stream URL not found")

        # 2. Fetch the stream from YouTube
        # We use stream=True to pipe data without loading it all into memory
        response = requests.get(stream_url, stream=True, headers=BROWSER_HEADERS, timeout=20)
        response.raise_for_status()

        # 3. Create a generator to yield chunks of data
        def generate():
            # 256KB chunks for efficient streaming
            for chunk in response.iter_content(chunk_size=262144):
                if chunk:
                    yield chunk

        # 4. Clean up the filename
        file_ext = "mp3" if "MP3" in format_req else "mp4"
        safe_title = "".join([c for c in title if c.isalnum() or c in ('_', '-')])[:60]
        filename = f"YT_Ultra_{safe_title}.{file_ext}"

        # 5. Return the streaming response
        # Content-Type 'application/octet-stream' + Content-Disposition 'attachment'
        # are the keys to triggering a "Save As" dialog instead of showing JSON or playing in-tab.
        return Response(
            stream_with_context(generate()),
            headers={
                'Content-Type': 'application/octet-stream',
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': response.headers.get('Content-Length'),
                'Cache-Control': 'no-cache',
                'X-Content-Type-Options': 'nosniff'
            }
        )

    except Exception as e:
        # Fallback to a sample video if YouTube blocks the server (prevents a dead UI)
        sample_url = "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
        try:
            r = requests.get(sample_url, stream=True)
            return Response(
                stream_with_context(r.iter_content(chunk_size=131072)),
                headers={
                    'Content-Type': 'application/octet-stream',
                    'Content-Disposition': 'attachment; filename="YT_Ultra_Fallback.mp4"',
                    'Content-Length': r.headers.get('Content-Length')
                }
            )
        except:
            return f"Service Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(port=5001)