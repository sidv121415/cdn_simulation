# 🌐 CDN Simulation with RTMP Streaming

**Python-based Content Delivery Network (CDN) simulation system** integrated with **RTMP streaming** capabilities for real-time video distribution.
This project demonstrates CDN principles including **content caching**, **distributed delivery**, and **live streaming** through an **nginx RTMP server** with **mobile camera support** and **real-time monitoring dashboards**.

---

## 🔍 What is This Project?

This project combines traditional CDN functionality with real-time video streaming infrastructure. It simulates how content delivery networks distribute and cache content across multiple edge servers while supporting **live RTMP streaming** from mobile devices.

**Key components:**

* Real-time monitoring dashboards for cache performance and stream analytics
* Control panel for managing edge servers and stream distribution
* nginx HLS server integration for converting RTMP to browser-compatible HLS streams
* 3D visualization of cache server locations and network topology
* Live video streaming using RTMP protocol from mobile cameras
* Performance metrics tracking: cache hit rates, bandwidth, and latency

It demonstrates how modern CDN infrastructure handles live video distribution at scale, similar to platforms like YouTube Live, Twitch, or video conferencing systems.

---

## 📁 Project Structure

```
cdn_simulation/
├── control_dashboard.py       # Control panel for CDN management
├── nginx_hls_server.py        # nginx RTMP/HLS server integration
├── visualization_dashboard.py # 3D visualization and analytics dashboard
└── README.md                  # Project documentation
```

**File Descriptions:**

* `control_dashboard.py` – Web-based dashboard for managing edge servers, monitoring cache performance, controlling stream distribution, and viewing real-time metrics.
* `nginx_hls_server.py` – Python integration layer that manages nginx RTMP server, handles mobile RTMP stream ingestion, converts streams to HLS format, distributes streams to edge servers, and monitors server health.
* `visualization_dashboard.py` – Interactive 3D visualization dashboard showing server locations, real-time performance graphs, network topology, and viewer analytics.

---

## ⚙️ Installation & Setup

### Prerequisites

* Python 3.8+
* nginx with RTMP module
* Mobile device with RTMP camera app
* Ubuntu/Debian Linux (recommended) or Windows

---

### Step 1: Install nginx with RTMP Module (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install build-essential libpcre3 libpcre3-dev libssl-dev zlib1g-dev git unzip

cd /usr/local/src
sudo wget http://nginx.org/download/nginx-1.26.0.tar.gz
sudo git clone https://github.com/arut/nginx-rtmp-module.git

sudo tar -zxvf nginx-1.26.0.tar.gz
cd nginx-1.26.0
sudo ./configure --with-http_ssl_module --add-module=../nginx-rtmp-module --with-http_flv_module --with-http_mp4_module
sudo make
sudo make install

# Verify
nginx -V 2>&1 | grep rtmp
```

---

### Step 2: Configure nginx for RTMP & HLS

Edit `/usr/local/nginx/conf/nginx.conf`:

```nginx
rtmp {
    server {
        listen 1935;
        chunk_size 4096;

        application live {
            live on;
            record off;
            hls on;
            hls_path /tmp/hls;
            hls_fragment 3;
            hls_playlist_length 60;
        }

        application mobile {
            live on;
            record off;
            hls on;
            hls_path /tmp/hls_mobile;
            hls_fragment 3;
            hls_playlist_length 60;
        }
    }
}

http {
    include mime.types;
    default_type application/octet-stream;

    server {
        listen 8080;
        add_header Access-Control-Allow-Origin *;

        location /hls {
            types { application/vnd.apple.mpegurl m3u8; video/mp2t ts; }
            root /tmp;
            add_header Cache-Control no-cache;
        }

        location /hls_mobile {
            types { application/vnd.apple.mpegurl m3u8; video/mp2t ts; }
            root /tmp;
            add_header Cache-Control no-cache;
        }

        location /dash { root /tmp; add_header Cache-Control no-cache; }
    }
}
```

Create HLS/DASH directories:

```bash
sudo mkdir -p /tmp/hls /tmp/hls_mobile /tmp/dash
sudo chmod -R 777 /tmp/hls /tmp/hls_mobile /tmp/dash
sudo /usr/local/nginx/sbin/nginx        # Start nginx
sudo /usr/local/nginx/sbin/nginx -s reload  # Reload after changes
```

---

### Step 3: Mobile Camera Setup

**Android apps:** RTMP Camera, Larix Broadcaster, CameraFi Live
**iOS apps:** Larix Broadcaster, Live Reporter, Livestream Producer

Configure server URL in the app:

```
rtmp://<SERVER_IP>:1935/mobile
Stream Key: <your_stream_name>
```

Open firewall ports (Ubuntu example):

```bash
sudo ufw allow 1935/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 5000/tcp  # Flask dashboards
sudo ufw reload
```

---

### Step 4: Run the CDN Simulation

```bash
git clone https://github.com/sidv121415/cdn_simulation.git
cd cdn_simulation
pip install flask flask-cors plotly dash pandas

# Start nginx integration
python nginx_hls_server.py &

# Start control dashboard
python control_dashboard.py &

# Start visualization dashboard
python visualization_dashboard.py
```

**Dashboard Access:**

* Control Dashboard: [http://localhost:5000](http://localhost:5000)
* Visualization Dashboard: [http://localhost:8050](http://localhost:8050)
* HLS Stream: `http://<SERVER_IP>:8080/hls_mobile/<stream_name>.m3u8`

---

## 📊 Dashboard Features

### Control Dashboard

* Add/remove edge servers, configure cache
* Start/stop streams, manage stream quality
* Clear caches, adjust eviction policies
* View real-time metrics: bandwidth, active viewers, cache hit rate
* Log viewer for system events

### Visualization Dashboard

* 3D globe showing edge server locations
* Real-time performance graphs (bandwidth, latency, hit rate)
* Network topology visualization
* Viewer distribution heatmaps

---

## ⚡ Troubleshooting

**Mobile camera cannot connect:**

```bash
ps aux | grep nginx
sudo netstat -tuln | grep 1935
tail -50 /usr/local/nginx/logs/error.log
```

**Stream not playing in browser:**

* Check HLS files in `/tmp/hls_mobile/`
* Verify nginx config: `sudo /usr/local/nginx/sbin/nginx -t`

**High latency:**

* Reduce `hls_fragment` to 1, `hls_playlist_length` to 20
* Lower mobile bitrate, use 720p, enable hardware encoding

**Dashboards not loading:**

* Ensure Python processes running (`ps aux | grep python`)
* Verify ports 5000/8050 are free

---

## 📈 Performance Metrics

| Metric                  | Description                           |
| ----------------------- | ------------------------------------- |
| Cache Hit Rate          | % of requests served from edge cache  |
| Stream Latency          | Delay between capture and playback    |
| Bandwidth Usage         | Total data across edge servers        |
| Active Viewers          | Concurrent viewers                    |
| Geographic Distribution | Viewer/request distribution by region |
| Server Load             | CPU/memory per edge server            |
| Segment Generation Rate | HLS segment creation frequency        |

---

## 🧰 Technologies Used

* Python 3.8+
* nginx with RTMP Module
* Flask (control dashboard)
* Dash/Plotly (visualization dashboard)
* RTMP Protocol / HLS streaming
* WebSockets (real-time updates)
* Three.js (3D visualization, optional)

---

## 🔮 Future Enhancements

* Redis caching layer for edge servers
* Adaptive bitrate streaming
* Stream recording and VOD playback
* Load balancing across multiple nginx instances
* Historical CDN analytics
* Stream authentication and access control
* Viewer chat integration
