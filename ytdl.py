from flask import Flask, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/info/<path:video_url>', methods=['GET'])
def get_video_info(video_url):
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        sanitized_info = ydl.sanitize_info(info)
    return jsonify(sanitized_info)

@app.route('/formats/<path:video_url>', methods=['GET'])
def get_formats(video_url):
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        formats = info.get('formats', [])
    return jsonify(formats)

@app.route('/extractors', methods=['GET'])
def list_extractors():
    with yt_dlp.YoutubeDL() as ydl:
        extractors = ydl.list_extractors()
    return jsonify(extractors)

@app.route('/version', methods=['GET'])
def get_version():
    return jsonify({'version': yt_dlp.version.__version__})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
