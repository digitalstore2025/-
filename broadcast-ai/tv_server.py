#!/usr/bin/env python3
"""
Quran-Conditioned Palestinian Broadcast AI — Web Streaming Server

Serves the latest generated TV segment over HTTP so it can be viewed in any
browser or embedded in a web page.

Routes
------
/           — HTML player page
/stream     — Direct video file (latest segment)
/health     — JSON health-check endpoint
"""

import os

from flask import Flask, Response, jsonify, send_file

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VIDEO_PATH = "output/tv_channel.mp4"
AUDIO_FALLBACK = "output/tv_audio.wav"
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 3000))

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = Flask(__name__)


@app.route("/")
def index():
    """Minimal HTML player page."""
    return Response(
        """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>صوت القدس — AI Palestinian Broadcast</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: 'Segoe UI', Tahoma, sans-serif;
    background: #0a0a0a;
    color: #e0e0e0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
  }
  h1 { margin-bottom: 1rem; font-size: 1.6rem; color: #00c853; }
  .player {
    background: #1a1a1a;
    border: 1px solid #333;
    border-radius: 12px;
    padding: 2rem;
    max-width: 720px;
    width: 90%;
    text-align: center;
  }
  video, audio { width: 100%; border-radius: 8px; margin-top: 1rem; }
  .status { margin-top: 1rem; font-size: 0.85rem; color: #888; }
</style>
</head>
<body>
  <div class="player">
    <h1>صوت القدس — AI Palestinian Broadcast</h1>
    <div id="media"></div>
    <p class="status" id="status">جاري التحميل...</p>
  </div>
  <script>
    const media = document.getElementById('media');
    const status = document.getElementById('status');
    fetch('/health').then(r => r.json()).then(data => {
      if (data.video) {
        media.innerHTML = '<video controls autoplay><source src="/stream" type="video/mp4"></video>';
        status.textContent = 'بث مباشر — فيديو';
      } else if (data.audio) {
        media.innerHTML = '<audio controls autoplay><source src="/stream" type="audio/wav"></audio>';
        status.textContent = 'بث مباشر — صوت';
      } else {
        status.textContent = 'لا يوجد بث حالياً. شغّل run_tv_channel.py أولاً.';
      }
    }).catch(() => {
      status.textContent = 'خطأ في الاتصال';
    });
  </script>
</body>
</html>""",
        content_type="text/html; charset=utf-8",
    )


@app.route("/stream")
def stream():
    """Serve the latest generated media file."""
    if os.path.exists(VIDEO_PATH):
        return send_file(
            os.path.abspath(VIDEO_PATH),
            mimetype="video/mp4",
        )
    if os.path.exists(AUDIO_FALLBACK):
        return send_file(
            os.path.abspath(AUDIO_FALLBACK),
            mimetype="audio/wav",
        )
    return Response("No media available yet", status=404)


@app.route("/health")
def health():
    """Health check — tells the frontend what media is available."""
    return jsonify(
        {
            "status": "ok",
            "video": os.path.exists(VIDEO_PATH),
            "audio": os.path.exists(AUDIO_FALLBACK),
        }
    )


if __name__ == "__main__":
    print(f"[SERVER] Palestinian AI Broadcast — http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=False)
