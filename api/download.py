
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/download', methods=['GET'])
def download():
    video_id = request.args.get('id')
    format_type = request.args.get('format', 'mp4')
    return jsonify({
        "status": "Ready",
        "id": video_id,
        "format": format_type,
        "message": "Backend stream initialized successfully."
    })

if __name__ == "__main__":
    app.run(port=5001)
