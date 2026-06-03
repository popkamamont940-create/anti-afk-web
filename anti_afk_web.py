#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anti-AFK for Roblox - Web Edition (Single File)
Author: Jakonchik
Run: python anti_afk_web.py
Then open http://localhost:8000
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random
import time
import threading
import uvicorn
from pynput.keyboard import Controller, Key

# ========== Backend Worker ==========
class AFKWorker:
    def __init__(self):
        self.keyboard = Controller()
        self.running = False
        self.thread = None
        self.mode = "space"
        self.min_interval = 10.0
        self.max_interval = 60.0
        self.press_count = 0
        self.last_interval = 0.0
        self.current_key = ""

    def start(self):
        if self.running:
            return False
        self.running = True
        self.press_count = 0
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        return True

    def update_settings(self, mode: str, min_int: float, max_int: float):
        self.mode = mode
        self.min_interval = max(0.5, min_int)
        self.max_interval = max(self.min_interval, max_int)

    def _worker(self):
        while self.running:
            if self.mode == "space":
                key = Key.space
                key_str = "Space"
            elif self.mode == "wasd":
                key = random.choice(['w', 'a', 's', 'd'])
                key_str = key.upper()
            else:  # mixed
                if random.choice([True, False]):
                    key = Key.space
                    key_str = "Space"
                else:
                    key = random.choice(['w', 'a', 's', 'd'])
                    key_str = key.upper()

            try:
                if isinstance(key, str):
                    self.keyboard.press(key)
                    time.sleep(0.05)
                    self.keyboard.release(key)
                else:
                    self.keyboard.press(key)
                    time.sleep(0.05)
                    self.keyboard.release(key)
            except Exception as e:
                print(f"Emulation error: {e}")

            self.press_count += 1
            self.current_key = key_str

            interval = random.uniform(self.min_interval, self.max_interval)
            self.last_interval = interval

            steps = int(interval * 10)
            for _ in range(steps):
                if not self.running:
                    break
                time.sleep(0.1)

    def get_status(self):
        return {
            "running": self.running,
            "mode": self.mode,
            "min_interval": self.min_interval,
            "max_interval": self.max_interval,
            "press_count": self.press_count,
            "last_interval": round(self.last_interval, 2),
            "current_key": self.current_key
        }

# ========== FastAPI App ==========
app = FastAPI(title="Anti-AFK Web")
worker = AFKWorker()
active_connections = []

class SettingsUpdate(BaseModel):
    mode: str
    min_interval: float
    max_interval: float

# Modern sleek HTML/CSS/JS (Dark theme with neon cyan accents)
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Anti-AFK · Roblox</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,600;14..32,700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: radial-gradient(circle at 20% 30%, #0a0a0f, #030308);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1rem;
            position: relative;
            overflow-x: hidden;
        }

        .glow-orb {
            position: fixed;
            width: 80vw;
            height: 80vw;
            background: radial-gradient(circle, rgba(0, 255, 255, 0.08) 0%, rgba(0, 0, 0, 0) 70%);
            border-radius: 50%;
            top: -20%;
            right: -20%;
            pointer-events: none;
            z-index: 0;
            animation: floatGlow 20s infinite alternate;
        }

        @keyframes floatGlow {
            0% { transform: translate(0, 0) scale(1); opacity: 0.4; }
            100% { transform: translate(-5%, -5%) scale(1.2); opacity: 0.7; }
        }

        .container {
            position: relative;
            z-index: 2;
            width: 100%;
            max-width: 560px;
        }

        .glass-panel {
            background: rgba(12, 12, 20, 0.65);
            backdrop-filter: blur(12px);
            border-radius: 2rem;
            border: 1px solid rgba(0, 255, 255, 0.2);
            padding: 2rem 1.8rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), 0 0 0 0.5px rgba(0, 255, 255, 0.1);
            transition: all 0.3s ease;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            flex-wrap: wrap;
            margin-bottom: 2rem;
            border-bottom: 1px solid rgba(0, 255, 255, 0.3);
            padding-bottom: 1rem;
        }

        h1 {
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #fff, #4affff);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }

        h1 span {
            font-weight: 300;
            font-size: 1rem;
            background: none;
            -webkit-background-clip: unset;
            background-clip: unset;
            color: #4affff;
        }

        .status-badge {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.3rem 0.8rem;
            border-radius: 2rem;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
            letter-spacing: 1px;
        }

        .led {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }

        .led.red {
            background: #ff3366;
            box-shadow: 0 0 6px #ff3366;
            animation: pulseRed 1.2s infinite;
        }

        .led.green {
            background: #4affff;
            box-shadow: 0 0 8px #4affff;
            animation: pulseGreen 0.8s infinite;
        }

        @keyframes pulseRed {
            0% { opacity: 0.4; transform: scale(0.8);}
            100% { opacity: 1; transform: scale(1.2);}
        }
        @keyframes pulseGreen {
            0% { opacity: 0.6; box-shadow: 0 0 0px #4affff;}
            100% { opacity: 1; box-shadow: 0 0 12px #4affff;}
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 1.2rem;
            padding: 1rem 0.5rem;
            text-align: center;
            border: 1px solid rgba(0, 255, 255, 0.2);
            transition: transform 0.2s;
        }

        .stat-card:hover {
            transform: translateY(-3px);
            border-color: rgba(0, 255, 255, 0.5);
        }

        .stat-label {
            font-size: 0.7rem;
            letter-spacing: 1px;
            color: #aaa;
            margin-bottom: 0.5rem;
        }

        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #4affff;
            text-shadow: 0 0 5px rgba(0, 255, 255, 0.5);
            font-family: monospace;
        }

        .control-group {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .btn {
            flex: 1;
            padding: 0.9rem;
            font-weight: 700;
            font-size: 1rem;
            letter-spacing: 1px;
            border: none;
            border-radius: 2rem;
            cursor: pointer;
            transition: all 0.2s;
            font-family: inherit;
            backdrop-filter: blur(4px);
        }

        .btn-primary {
            background: linear-gradient(90deg, #00c6ff, #0072ff);
            color: white;
            box-shadow: 0 4px 12px rgba(0, 114, 255, 0.3);
        }
        .btn-primary:hover {
            transform: scale(1.02);
            box-shadow: 0 6px 18px rgba(0, 114, 255, 0.5);
        }

        .btn-secondary {
            background: rgba(30, 30, 50, 0.8);
            color: #eee;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .btn-secondary:hover {
            background: rgba(50, 50, 80, 0.9);
            transform: scale(1.02);
        }

        .settings-section {
            margin-bottom: 1.8rem;
        }
        .settings-section h3 {
            font-size: 0.85rem;
            letter-spacing: 1.5px;
            color: #ccc;
            margin-bottom: 1rem;
            font-weight: 600;
        }

        .mode-selector {
            display: flex;
            gap: 0.8rem;
            flex-wrap: wrap;
        }
        .mode-option {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 2rem;
            padding: 0.5rem 1rem;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .mode-option input {
            display: none;
        }
        .mode-option span {
            font-size: 0.85rem;
            font-weight: 500;
        }
        .mode-option:has(input:checked) {
            background: #0072ff;
            border-color: #4affff;
            box-shadow: 0 0 8px #0072ff;
        }
        .mode-option:has(input:checked) span {
            color: white;
        }

        .dual-slider {
            margin-bottom: 1rem;
        }
        .slider-label {
            display: flex;
            justify-content: space-between;
            font-size: 0.75rem;
            color: #aaa;
            margin: 0.5rem 0 0.2rem;
        }
        input[type="range"] {
            width: 100%;
            height: 4px;
            -webkit-appearance: none;
            background: #2a2a3a;
            border-radius: 2px;
            margin: 0.5rem 0;
        }
        input[type="range"]:focus {
            outline: none;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #4affff;
            cursor: pointer;
            box-shadow: 0 0 6px #4affff;
        }

        .interval-inputs {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin-top: 0.5rem;
        }
        .interval-inputs input {
            background: rgba(0,0,0,0.6);
            border: 1px solid #2a2a3a;
            border-radius: 1rem;
            padding: 0.5rem 0.8rem;
            color: #fff;
            width: 100px;
            text-align: center;
            font-family: monospace;
        }
        .interval-inputs span {
            color: #4affff;
        }

        .footer {
            margin-top: 2rem;
            text-align: center;
            font-size: 0.7rem;
            color: #888;
        }
        .hotkey {
            background: rgba(0, 255, 255, 0.1);
            display: inline-block;
            padding: 0.3rem 1rem;
            border-radius: 2rem;
            margin-bottom: 0.5rem;
            font-weight: 600;
            font-size: 0.7rem;
            letter-spacing: 1px;
        }
        .warning {
            color: #ff9966;
            font-size: 0.7rem;
            margin-bottom: 0.5rem;
        }
        .credits {
            margin-top: 0.8rem;
            color: #aaa;
            font-size: 0.7rem;
        }
        .credits strong {
            color: #4affff;
        }

        @media (max-width: 500px) {
            .glass-panel { padding: 1.5rem; }
            .stat-value { font-size: 1.2rem; }
            h1 { font-size: 1.4rem; }
        }
    </style>
</head>
<body>
    <div class="glow-orb"></div>
    <div class="container">
        <div class="glass-panel">
            <div class="header">
                <h1>⚡ ANTI-AFK <span>ROBLOX</span></h1>
                <div class="status-badge" id="statusBadge">
                    <span class="led red"></span> STOPPED
                </div>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">PRESSES</div>
                    <div class="stat-value" id="pressCount">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">LAST KEY</div>
                    <div class="stat-value" id="lastKey">—</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">LAST INTERVAL</div>
                    <div class="stat-value" id="lastInterval">0.00</div>
                </div>
            </div>

            <div class="control-group">
                <button id="startBtn" class="btn btn-primary">▶ START</button>
                <button id="stopBtn" class="btn btn-secondary">⏹ STOP</button>
            </div>

            <div class="settings-section">
                <h3>KEY PRESS MODE</h3>
                <div class="mode-selector">
                    <label class="mode-option">
                        <input type="radio" name="mode" value="space" checked> <span>🔘 SPACE</span>
                    </label>
                    <label class="mode-option">
                        <input type="radio" name="mode" value="wasd"> <span>🎮 WASD</span>
                    </label>
                    <label class="mode-option">
                        <input type="radio" name="mode" value="mixed"> <span>🌀 MIXED</span>
                    </label>
                </div>
            </div>

            <div class="settings-section">
                <h3>INTERVAL (SECONDS)</h3>
                <div class="dual-slider">
                    <div class="slider-label">
                        <span>Min</span>
                        <span id="minValue">10.0</span>
                    </div>
                    <input type="range" id="minSlider" min="1" max="120" step="0.5" value="10">
                    <div class="slider-label">
                        <span>Max</span>
                        <span id="maxValue">60.0</span>
                    </div>
                    <input type="range" id="maxSlider" min="1" max="120" step="0.5" value="60">
                </div>
                <div class="interval-inputs">
                    <input type="number" id="minInput" step="0.5" value="10">
                    <span>—</span>
                    <input type="number" id="maxInput" step="0.5" value="60">
                </div>
            </div>

            <div class="footer">
                <div class="hotkey">⚡ SPACE — START / STOP</div>
                <div class="warning">⚠️ Admin rights may be required for Roblox</div>
                <div class="credits">Made by <strong>Jakonchik</strong> · Web Developer</div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let reconnectTimer = null;
        let statusCheckInterval = null;

        const elements = {
            startBtn: document.getElementById('startBtn'),
            stopBtn: document.getElementById('stopBtn'),
            statusBadge: document.getElementById('statusBadge'),
            pressCount: document.getElementById('pressCount'),
            lastKey: document.getElementById('lastKey'),
            lastInterval: document.getElementById('lastInterval'),
            minSlider: document.getElementById('minSlider'),
            maxSlider: document.getElementById('maxSlider'),
            minInput: document.getElementById('minInput'),
            maxInput: document.getElementById('maxInput'),
            minValue: document.getElementById('minValue'),
            maxValue: document.getElementById('maxValue'),
            modeRadios: document.querySelectorAll('input[name="mode"]')
        };

        let currentStatus = {
            running: false,
            press_count: 0,
            current_key: '—',
            last_interval: 0,
            mode: 'space',
            min_interval: 10,
            max_interval: 60
        };

        async function apiStart() {
            try {
                const res = await fetch('/api/start', { method: 'POST' });
                if (res.ok) fetchStatus();
            } catch(e) { console.error(e); }
        }

        async function apiStop() {
            try {
                const res = await fetch('/api/stop', { method: 'POST' });
                if (res.ok) fetchStatus();
            } catch(e) { console.error(e); }
        }

        async function updateSettings() {
            const mode = document.querySelector('input[name="mode"]:checked').value;
            const min = parseFloat(elements.minSlider.value);
            const max = parseFloat(elements.maxSlider.value);
            try {
                await fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mode, min_interval: min, max_interval: max })
                });
            } catch(e) { console.error(e); }
        }

        async function fetchStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                applyStatus(data);
            } catch(e) { console.warn('Status fetch failed', e); }
        }

        function applyStatus(data) {
            currentStatus = { ...currentStatus, ...data };
            elements.pressCount.innerText = data.press_count || 0;
            elements.lastKey.innerText = data.current_key || '—';
            elements.lastInterval.innerText = (data.last_interval || 0).toFixed(2);
            
            if (data.running) {
                elements.statusBadge.innerHTML = '<span class="led green"></span> ACTIVE';
                elements.startBtn.disabled = true;
                elements.stopBtn.disabled = false;
            } else {
                elements.statusBadge.innerHTML = '<span class="led red"></span> STOPPED';
                elements.startBtn.disabled = false;
                elements.stopBtn.disabled = true;
            }
            
            if (data.min_interval !== undefined) {
                elements.minSlider.value = data.min_interval;
                elements.minInput.value = data.min_interval;
                elements.minValue.innerText = data.min_interval.toFixed(1);
                elements.maxSlider.value = data.max_interval;
                elements.maxInput.value = data.max_interval;
                elements.maxValue.innerText = data.max_interval.toFixed(1);
            }
            if (data.mode) {
                const radio = document.querySelector(`input[name="mode"][value="${data.mode}"]`);
                if (radio) radio.checked = true;
            }
        }

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                console.log('WebSocket connected');
                if (reconnectTimer) clearTimeout(reconnectTimer);
            };
            
            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'pong') return;
                    applyStatus(data);
                } catch(e) {}
            };
            
            ws.onclose = () => {
                console.log('WebSocket closed, reconnecting...');
                reconnectTimer = setTimeout(connectWebSocket, 2000);
            };
            
            ws.onerror = (err) => {
                console.warn('WebSocket error', err);
            };
        }

        function syncSliders() {
            let minVal = parseFloat(elements.minSlider.value);
            let maxVal = parseFloat(elements.maxSlider.value);
            if (minVal > maxVal) {
                if (document.activeElement === elements.minSlider) {
                    elements.maxSlider.value = minVal;
                    maxVal = minVal;
                } else {
                    elements.minSlider.value = maxVal;
                    minVal = maxVal;
                }
            }
            elements.minValue.innerText = minVal.toFixed(1);
            elements.maxValue.innerText = maxVal.toFixed(1);
            elements.minInput.value = minVal;
            elements.maxInput.value = maxVal;
            updateSettings();
        }

        function syncFromInputs() {
            let minVal = parseFloat(elements.minInput.value);
            let maxVal = parseFloat(elements.maxInput.value);
            if (isNaN(minVal)) minVal = 1;
            if (isNaN(maxVal)) maxVal = 60;
            if (minVal < 0.5) minVal = 0.5;
            if (maxVal < minVal) maxVal = minVal;
            elements.minSlider.value = minVal;
            elements.maxSlider.value = maxVal;
            syncSliders();
        }

        function onModeChange() {
            updateSettings();
        }

        function handleKeyDown(e) {
            if (e.code === 'Space' && !e.target.matches('input, textarea, button')) {
                e.preventDefault();
                if (currentStatus.running) {
                    apiStop();
                } else {
                    apiStart();
                }
            }
        }

        function init() {
            connectWebSocket();
            fetchStatus();
            statusCheckInterval = setInterval(fetchStatus, 2000);
            
            elements.startBtn.addEventListener('click', apiStart);
            elements.stopBtn.addEventListener('click', apiStop);
            elements.minSlider.addEventListener('input', syncSliders);
            elements.maxSlider.addEventListener('input', syncSliders);
            elements.minInput.addEventListener('change', syncFromInputs);
            elements.maxInput.addEventListener('change', syncFromInputs);
            elements.modeRadios.forEach(radio => radio.addEventListener('change', onModeChange));
            window.addEventListener('keydown', handleKeyDown);
        }

        init();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return HTML_PAGE

@app.get("/api/status")
async def get_status():
    return worker.get_status()

@app.post("/api/start")
async def start_afk():
    if not worker.running:
        worker.start()
        await broadcast_status()
    return {"success": True}

@app.post("/api/stop")
async def stop_afk():
    if worker.running:
        worker.stop()
        await broadcast_status()
    return {"success": True}

@app.post("/api/settings")
async def update_settings(settings: SettingsUpdate):
    if settings.mode not in ["space", "wasd", "mixed"]:
        raise HTTPException(status_code=400, detail="Invalid mode")
    if settings.min_interval <= 0 or settings.max_interval <= 0 or settings.min_interval > settings.max_interval:
        raise HTTPException(status_code=400, detail="Invalid interval")
    worker.update_settings(settings.mode, settings.min_interval, settings.max_interval)
    await broadcast_status()
    return {"success": True}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        await websocket.send_json(worker.get_status())
        while True:
            await websocket.receive_text()
            await websocket.send_json(worker.get_status())
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def broadcast_status():
    if not active_connections:
        return
    status = worker.get_status()
    for conn in active_connections[:]:
        try:
            await conn.send_json(status)
        except:
            active_connections.remove(conn)

# ========== Run Server ==========
if __name__ == "__main__":
    import asyncio
    print("=" * 50)
    print("🔥 Anti-AFK Web Edition (Single File)")
    print("👤 Made by Jakonchik")
    print("🌐 Open http://localhost:8000 in your browser")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
