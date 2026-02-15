#!/usr/bin/env python3
"""
Quran-Conditioned Palestinian Broadcast AI — Web Streaming Server

Full-featured broadcast web platform with:
- Live TV player (video + audio fallback)
- Radio stream endpoint
- Podcast episodes browser
- Broadcast schedule display
- Dashboard with system stats
- REST API for programmatic access
- Voiceover generation API

Routes
------
/               — Main broadcast player
/radio          — Radio-only player
/podcasts       — Podcast episodes browser
/schedule       — Broadcast schedule view
/dashboard      — System dashboard

/api/stream     — Direct media file
/api/radio      — Radio audio stream
/api/health     — Health check
/api/schedule   — Schedule JSON
/api/history    — Segment history JSON
/api/generate   — On-demand TTS generation (POST)
/api/episodes   — Podcast episodes list
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_file

import config
from logger import get_logger
from scheduler import get_current_block, get_next_block_change, get_schedule_display

log = get_logger("server")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = Flask(__name__)

_start_time = time.time()


# ---------------------------------------------------------------------------
# HTML Templates
# ---------------------------------------------------------------------------

_CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body {
  font-family: 'Segoe UI', Tahoma, sans-serif;
  background: #0a0a0a;
  color: #e0e0e0;
  min-height: 100vh;
  direction: rtl;
}
.container { max-width: 960px; margin: 0 auto; padding: 1.5rem; }
nav {
  background: #111;
  border-bottom: 2px solid #00c853;
  padding: 0.8rem 1.5rem;
  display: flex;
  gap: 1.5rem;
  align-items: center;
  flex-wrap: wrap;
}
nav a {
  color: #aaa;
  text-decoration: none;
  font-size: 0.95rem;
  transition: color 0.2s;
}
nav a:hover, nav a.active { color: #00c853; }
nav .brand {
  color: #00c853;
  font-weight: bold;
  font-size: 1.1rem;
  margin-left: auto;
}
h1 { color: #00c853; font-size: 1.5rem; margin-bottom: 1rem; }
h2 { color: #00c853; font-size: 1.2rem; margin: 1.5rem 0 0.8rem; }
.card {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}
video, audio { width: 100%; border-radius: 8px; margin-top: 1rem; }
.badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
}
.badge-live { background: #c62828; color: #fff; }
.badge-news { background: #1565c0; color: #fff; }
.badge-quran { background: #2e7d32; color: #fff; }
.badge-radio { background: #6a1b9a; color: #fff; }
.badge-podcast { background: #e65100; color: #fff; }
.status { color: #888; font-size: 0.85rem; margin-top: 0.5rem; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
@media (max-width: 600px) { .grid { grid-template-columns: 1fr; } }
.schedule-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #222;
}
.schedule-row:last-child { border-bottom: none; }
.stat-num { font-size: 2rem; font-weight: bold; color: #00c853; }
.stat-label { font-size: 0.85rem; color: #888; }
table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; }
th, td { padding: 0.5rem; text-align: right; border-bottom: 1px solid #222; }
th { color: #00c853; font-size: 0.85rem; }
"""

_NAV = """
<nav>
  <span class="brand">صوت القدس AI</span>
  <a href="/">البث المباشر</a>
  <a href="/radio">الراديو</a>
  <a href="/podcasts">بودكاست</a>
  <a href="/schedule">الجدول</a>
  <a href="/dashboard">لوحة التحكم</a>
</nav>
"""


def _page(title: str, body: str) -> Response:
    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — صوت القدس AI</title>
<style>{_CSS}</style>
</head>
<body>
{_NAV}
<div class="container">
{body}
</div>
</body>
</html>"""
    return Response(html, content_type="text/html; charset=utf-8")


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return _page("البث المباشر", """
<h1>البث المباشر <span class="badge badge-live">LIVE</span></h1>
<div class="card">
  <div id="media"></div>
  <p class="status" id="status">جاري التحميل...</p>
  <p class="status" id="schedule-info"></p>
</div>
<script>
const media = document.getElementById('media');
const status = document.getElementById('status');
const schedInfo = document.getElementById('schedule-info');

fetch('/api/health').then(r=>r.json()).then(data=>{
  if(data.video){
    media.innerHTML='<video controls autoplay><source src="/api/stream" type="video/mp4"></video>';
    status.textContent='بث مباشر — فيديو';
  } else if(data.audio){
    media.innerHTML='<audio controls autoplay><source src="/api/stream" type="audio/wav"></audio>';
    status.textContent='بث مباشر — صوت';
  } else {
    status.textContent='لا يوجد بث حالياً. شغّل run_tv_channel.py أولاً.';
  }
  if(data.schedule){
    schedInfo.textContent='البرنامج الحالي: '+data.schedule.current_label+' | القادم: '+data.schedule.next_label+' بعد '+data.schedule.minutes_until+' دقيقة';
  }
}).catch(()=>{status.textContent='خطأ في الاتصال';});
</script>
""")


@app.route("/radio")
def radio_page():
    return _page("الراديو", """
<h1>إذاعة صوت القدس</h1>
<div class="card">
  <audio controls autoplay>
    <source src="/api/radio" type="audio/wav">
  </audio>
  <p class="status">بث إذاعي مباشر</p>
</div>
""")


@app.route("/podcasts")
def podcasts_page():
    return _page("بودكاست", """
<h1>حلقات البودكاست</h1>
<div id="episodes" class="card">
  <p class="status">جاري تحميل الحلقات...</p>
</div>
<script>
fetch('/api/episodes').then(r=>r.json()).then(data=>{
  const el=document.getElementById('episodes');
  if(!data.episodes||data.episodes.length===0){
    el.innerHTML='<p class="status">لا توجد حلقات بعد. شغّل podcast_generator.py لإنشاء حلقات.</p>';
    return;
  }
  let html='';
  data.episodes.forEach((ep,i)=>{
    html+=`<div style="margin-bottom:1rem;padding-bottom:1rem;border-bottom:1px solid #222">
      <strong>حلقة ${i+1}</strong> — <span class="status">${ep.name}</span>
      <audio controls style="width:100%;margin-top:0.5rem"><source src="/api/episode/${ep.name}" type="audio/wav"></audio>
    </div>`;
  });
  el.innerHTML=html;
}).catch(()=>{document.getElementById('episodes').innerHTML='<p class="status">خطأ في التحميل</p>';});
</script>
""")


@app.route("/schedule")
def schedule_page():
    schedule = get_schedule_display()
    rows = ""
    for block in schedule:
        badge_cls = f"badge-{block['type']}" if block['type'] in ('news','quran','radio','podcast') else 'badge-news'
        rows += f"""<div class="schedule-row">
          <span>{block['start']} — {block['end']}</span>
          <span class="badge {badge_cls}">{block['label']}</span>
        </div>"""

    return _page("جدول البث", f"""
<h1>جدول البث اليومي</h1>
<div class="card">{rows}</div>
""")


@app.route("/dashboard")
def dashboard_page():
    return _page("لوحة التحكم", """
<h1>لوحة التحكم</h1>
<div class="grid" id="stats">
  <div class="card"><p class="status">جاري التحميل...</p></div>
</div>
<h2>آخر المقاطع</h2>
<div id="history" class="card">
  <p class="status">جاري التحميل...</p>
</div>
<script>
fetch('/api/health').then(r=>r.json()).then(data=>{
  document.getElementById('stats').innerHTML=`
    <div class="card"><div class="stat-num">${data.uptime_min}m</div><div class="stat-label">وقت التشغيل</div></div>
    <div class="card"><div class="stat-num">${data.segments_generated}</div><div class="stat-label">مقاطع تم إنشاؤها</div></div>
    <div class="card"><div class="stat-num">${data.schedule.current_label}</div><div class="stat-label">البرنامج الحالي</div></div>
    <div class="card"><div class="stat-num">${data.video?'نعم':'لا'}</div><div class="stat-label">فيديو متوفر</div></div>
  `;
});
fetch('/api/history').then(r=>r.json()).then(data=>{
  const el=document.getElementById('history');
  if(!data.history||data.history.length===0){
    el.innerHTML='<p class="status">لا توجد مقاطع بعد</p>';
    return;
  }
  let html='<table><tr><th>الوقت</th><th>النوع</th><th>النص</th><th>المدة</th></tr>';
  data.history.slice(-20).reverse().forEach(s=>{
    const t=new Date(s.timestamp).toLocaleTimeString('ar-EG');
    html+=`<tr><td>${t}</td><td><span class="badge badge-${s.style}">${s.style}</span></td><td>${s.text}</td><td>${s.duration}s</td></tr>`;
  });
  html+='</table>';
  el.innerHTML=html;
});
</script>
""")


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@app.route("/api/stream")
def api_stream():
    video = config.OUTPUT_DIR / "tv_channel.mp4"
    audio = config.OUTPUT_DIR / "tv_audio.wav"

    if video.exists():
        return send_file(str(video.resolve()), mimetype="video/mp4")
    if audio.exists():
        return send_file(str(audio.resolve()), mimetype="audio/wav")
    return Response("No media available", status=404)


@app.route("/api/radio")
def api_radio():
    radio = config.OUTPUT_DIR / "radio_live.wav"
    audio = config.OUTPUT_DIR / "tv_audio.wav"

    if radio.exists():
        return send_file(str(radio.resolve()), mimetype="audio/wav")
    if audio.exists():
        return send_file(str(audio.resolve()), mimetype="audio/wav")
    return Response("No radio stream available", status=404)


@app.route("/api/health")
def api_health():
    video = config.OUTPUT_DIR / "tv_channel.mp4"
    audio = config.OUTPUT_DIR / "tv_audio.wav"
    history_file = config.OUTPUT_DIR / "segment_history.json"

    segments = 0
    if history_file.exists():
        try:
            segments = len(json.loads(history_file.read_text(encoding="utf-8")))
        except Exception:
            pass

    return jsonify({
        "status": "ok",
        "video": video.exists(),
        "audio": audio.exists(),
        "uptime_min": round((time.time() - _start_time) / 60, 1),
        "segments_generated": segments,
        "schedule": get_next_block_change(),
        "timestamp": datetime.now().isoformat(),
    })


@app.route("/api/schedule")
def api_schedule():
    return jsonify({
        "schedule": get_schedule_display(),
        "current": get_next_block_change(),
    })


@app.route("/api/history")
def api_history():
    history_file = config.OUTPUT_DIR / "segment_history.json"
    history = []
    if history_file.exists():
        try:
            history = json.loads(history_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return jsonify({"history": history})


@app.route("/api/episodes")
def api_episodes():
    episodes_dir = config.OUTPUT_DIR / "episodes"
    episodes = []
    if episodes_dir.exists():
        for f in sorted(episodes_dir.glob("*.wav")):
            episodes.append({
                "name": f.name,
                "size_mb": round(f.stat().st_size / 1024 / 1024, 1),
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            })
    return jsonify({"episodes": episodes})


@app.route("/api/episode/<name>")
def api_episode(name: str):
    # Prevent path traversal
    if "/" in name or "\\" in name or ".." in name:
        return Response("Invalid filename", status=400)
    path = config.OUTPUT_DIR / "episodes" / name
    if path.exists():
        return send_file(str(path.resolve()), mimetype="audio/wav")
    return Response("Episode not found", status=404)


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """On-demand TTS generation via API.

    POST JSON: {"text": "...", "style": "news"}
    Returns: {"success": true, "data": {"path": "...", "duration": ..., "style": "..."}}
    """
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"success": False, "error": "Missing 'text' field"}), 400

    text = data["text"]
    style = data.get("style", "news")
    output_name = data.get("output", f"api_{int(time.time())}.wav")

    # Prevent path traversal
    if "/" in output_name or "\\" in output_name or ".." in output_name:
        return jsonify({"success": False, "error": "Invalid output name"}), 400

    try:
        from generate import generate_voice
        t0 = time.time()
        path = generate_voice(text, style=style, output_name=output_name)
        duration = round(time.time() - t0, 1)
        return jsonify({"success": True, "data": {"path": path, "duration": duration, "style": style}})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    log.info("Palestinian AI Broadcast Server — http://%s:%d", config.SERVER_HOST, config.SERVER_PORT)
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=False)
