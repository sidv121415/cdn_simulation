from flask import Flask, render_template_string, jsonify, Response, request
from flask_cors import CORS
import time
import logging
from datetime import datetime
import requests
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
WINDOWS_IP = "172.16.13.136"
NGINX_HLS_URL = f'http://{WINDOWS_IP}:8080/hls'

# Viewer tracking
viewer_last_seen = {}
VIEWER_TIMEOUT = 10

request_count = 0
total_segment_requests = 0
start_time = datetime.now()

def cleanup_inactive_viewers():
    while True:
        try:
            current_time = time.time()
            inactive = [vid for vid, last_seen in viewer_last_seen.items() 
                       if current_time - last_seen > VIEWER_TIMEOUT]
            for vid in inactive:
                del viewer_last_seen[vid]
        except:
            pass
        time.sleep(5)

cleanup_thread = threading.Thread(target=cleanup_inactive_viewers, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stream</title>
        <link href="https://vjs.zencdn.net/8.5.2/video-js.css" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #000;
                color: #fff;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                overflow-x: hidden;
            }
            
            /* Animated background */
            body::before {
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: radial-gradient(ellipse at top, #1a1a2e 0%, #0f0f1e 50%, #000 100%);
                z-index: -1;
            }
            
            /* Floating gradient orbs */
            .orb {
                position: fixed;
                border-radius: 50%;
                filter: blur(80px);
                opacity: 0.15;
                animation: float 20s ease-in-out infinite;
                z-index: 0;
            }
            
            .orb1 {
                width: 500px;
                height: 500px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                top: -250px;
                left: -250px;
                animation-delay: 0s;
            }
            
            .orb2 {
                width: 400px;
                height: 400px;
                background: linear-gradient(135deg, #f093fb, #f5576c);
                bottom: -200px;
                right: -200px;
                animation-delay: 5s;
            }
            
            .orb3 {
                width: 350px;
                height: 350px;
                background: linear-gradient(135deg, #4facfe, #00f2fe);
                top: 50%;
                right: -175px;
                animation-delay: 10s;
            }
            
            @keyframes float {
                0%, 100% { transform: translate(0, 0) scale(1); }
                33% { transform: translate(30px, -30px) scale(1.1); }
                66% { transform: translate(-20px, 20px) scale(0.9); }
            }
            
            header {
                position: relative;
                padding: 40px 60px;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(40px);
                border-bottom: 1px solid rgba(255,255,255,0.03);
                z-index: 10;
            }
            
            h1 {
                margin: 0;
                font-size: 48px;
                font-weight: 700;
                background: linear-gradient(135deg, #fff 0%, #667eea 50%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -2px;
                animation: glow 3s ease-in-out infinite;
            }
            
            @keyframes glow {
                0%, 100% { filter: drop-shadow(0 0 20px rgba(102, 126, 234, 0.5)); }
                50% { filter: drop-shadow(0 0 40px rgba(118, 75, 162, 0.8)); }
            }
            
            .live-indicator {
                display: inline-flex;
                align-items: center;
                gap: 10px;
                padding: 10px 20px;
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.3);
                border-radius: 25px;
                font-size: 14px;
                font-weight: 600;
                color: #ef4444;
                margin-top: 15px;
                box-shadow: 0 0 30px rgba(239, 68, 68, 0.2);
            }
            
            .live-dot {
                width: 10px;
                height: 10px;
                background: #ef4444;
                border-radius: 50%;
                animation: pulse 2s ease-in-out infinite;
                box-shadow: 0 0 15px rgba(239, 68, 68, 0.8);
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.6; transform: scale(1.2); }
            }
            
            .container {
                position: relative;
                max-width: 1600px;
                margin: 0 auto;
                padding: 80px 60px;
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 5;
            }
            
            .video-wrapper {
                width: 100%;
                position: relative;
            }
            
            /* Glowing border effect */
            .video-glow {
                position: absolute;
                top: -20px;
                left: -20px;
                right: -20px;
                bottom: -20px;
                background: linear-gradient(135deg, #667eea, #764ba2, #f093fb, #4facfe);
                border-radius: 30px;
                opacity: 0.3;
                filter: blur(40px);
                animation: rotate 8s linear infinite;
                z-index: -1;
            }
            
            @keyframes rotate {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .video-container {
                position: relative;
                padding-bottom: 56.25%;
                height: 0;
                background: #000;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 
                    0 30px 80px rgba(0,0,0,0.8),
                    0 0 100px rgba(102, 126, 234, 0.2);
            }
            
            .video-container video {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
            }
            
            /* Custom video.js styles - FIXED CONTROLS */
            .vjs-big-play-button {
                border: none;
                background: linear-gradient(135deg, #667eea, #764ba2) !important;
                border-radius: 50%;
                width: 100px;
                height: 100px;
                line-height: 100px;
                margin-top: -50px;
                margin-left: -50px;
                font-size: 50px;
                box-shadow: 0 10px 40px rgba(102, 126, 234, 0.5);
                transition: all 0.4s ease;
            }
            
            .vjs-big-play-button:hover {
                background: linear-gradient(135deg, #764ba2, #667eea) !important;
                transform: scale(1.1);
                box-shadow: 0 15px 60px rgba(102, 126, 234, 0.8);
            }
            
            /* Control bar visibility */
            .video-js .vjs-control-bar {
                background: linear-gradient(to top, rgba(0,0,0,0.9), transparent) !important;
                backdrop-filter: blur(10px);
                display: flex !important;
            }
            
            .video-js .vjs-control {
                color: #fff !important;
                opacity: 1 !important;
            }
            
            .video-js .vjs-button > .vjs-icon-placeholder:before {
                color: #fff !important;
            }
            
            .video-js .vjs-play-progress {
                background: linear-gradient(135deg, #667eea, #764ba2) !important;
            }
            
            .video-js .vjs-volume-level {
                background: linear-gradient(135deg, #667eea, #764ba2) !important;
            }
            
            .video-js .vjs-slider {
                background: rgba(255,255,255,0.2) !important;
            }
            
            .video-js .vjs-load-progress {
                background: rgba(255,255,255,0.3) !important;
            }
            
            /* Ensure controls are always visible when needed */
            .video-js:hover .vjs-control-bar,
            .video-js.vjs-user-active .vjs-control-bar,
            .video-js.vjs-paused .vjs-control-bar {
                opacity: 1 !important;
                visibility: visible !important;
            }
            
            /* Subtle particle effect */
            @keyframes particle {
                0% { transform: translateY(0) translateX(0) scale(0); opacity: 0; }
                50% { opacity: 1; }
                100% { transform: translateY(-100vh) translateX(50px) scale(1); opacity: 0; }
            }
            
            .particle {
                position: fixed;
                width: 3px;
                height: 3px;
                background: rgba(102, 126, 234, 0.5);
                border-radius: 50%;
                pointer-events: none;
                z-index: 1;
            }
        </style>
    </head>
    <body>
        <div class="orb orb1"></div>
        <div class="orb orb2"></div>
        <div class="orb orb3"></div>
        
        <header style="text-align: center;">
            <h1>Stream</h1
            <div class="live-indicator">
                <span class="live-dot"></span>
                <span>LIVE BROADCAST</span>
            </div>
        </header>
        
        <div class="container">
            <div class="video-wrapper">
                <div class="video-glow"></div>
                <div class="video-container">
                    <video id="player" class="video-js vjs-default-skin vjs-big-play-centered" 
                           controls autoplay muted data-setup='{}'>
                        <source src="http://localhost:5000/stream/mobile.m3u8" 
                                type="application/x-mpegURL">
                    </video>
                </div>
            </div>
        </div>

        <script src="https://vjs.zencdn.net/8.5.2/video.min.js"></script>
        <script>
            var player = videojs('player', {
                liveui: true,
                liveTracker: { trackingThreshold: 0, liveTolerance: 2 },
                controlBar: {
                    volumePanel: { inline: false }
                }
            });
            
            // Ensure controls are always accessible
            player.ready(function() {
                this.controlBar.show();
            });
            
            // Create floating particles
            function createParticle() {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.bottom = '0';
                particle.style.animationDuration = (Math.random() * 3 + 2) + 's';
                particle.style.animationName = 'particle';
                document.body.appendChild(particle);
                
                setTimeout(() => particle.remove(), 5000);
            }
            
            setInterval(createParticle, 500);
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/stats')
def stats():
    uptime = str(datetime.now() - start_time).split('.')[0]
    return jsonify({
        'active_viewers': len(viewer_last_seen),
        'total_requests': request_count,
        'segment_requests': total_segment_requests,
        'uptime': uptime
    })

@app.route('/stream/<path:filename>')
def serve_stream(filename):
    global request_count, total_segment_requests
    request_count += 1
    
    viewer_id = request.args.get('viewer_id', 'unknown')
    if viewer_id != 'unknown':
        viewer_last_seen[viewer_id] = time.time()
    
    if filename.endswith('.ts'):
        total_segment_requests += 1
        time.sleep(0.85)
    
    nginx_url = f'{NGINX_HLS_URL}/{filename}'
    
    try:
        response = requests.get(nginx_url, timeout=5)
        
        if response.status_code == 200:
            if filename.endswith('.m3u8'):
                mimetype = 'application/vnd.apple.mpegurl'
            elif filename.endswith('.ts'):
                mimetype = 'video/mp2t'
            else:
                mimetype = 'application/octet-stream'
            
            return Response(response.content, 
                          mimetype=mimetype,
                          headers={
                              'Cache-Control': 'no-cache, no-store, must-revalidate',
                              'Access-Control-Allow-Origin': '*'
                          })
        else:
            return "Not found", 404
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("EdgeStream Origin Server")
    print("="*70)
    print("🌐 http://localhost:5000/")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
