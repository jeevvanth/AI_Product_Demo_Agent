import asyncio
from playwright.async_api import async_playwright
from aiohttp import web
import socketio
from livekit.api import AccessToken,VideoGrants
from livekit import rtc,api
import os
import io
import time
from datetime import datetime
from PIL import Image
import sounddevice as sd
import asyncio as _asyncio
from helper import create_browser_context,voice_generation,is_demo_intent,narrate_step,narrate_with_ws,narrate
from config import runner,BLOCK,CHANNEL,SAMPLE_RATE,LIVEKIT_API_KEY,LIVEKIT_API_SECRET,LIVEKIT_URL,connect_ws
# from agent_voice_process import mic_cb,spk_cb,send_mic_audio,monitor_playback,spk_q,mic_q,playback_buf,STATE,latest_transcript_event
from run_demo import run,run_the_demo
import queue
import tempfile
from pathlib import Path
import subprocess
# from voice_process import speak
# from realtime_websocket import RealtimeTTS
from cursor import click_with_cursor, inject_cursor_styles,set_cursor_mode
from agent_instruction import DemoAgent,publish_screen_share_lk
from livekit.agents import (
    AgentSession, 
    Agent, 
    room_io,
    JobContext,
    WorkerOptions,
    cli,
    AgentServer
)
from livekit.plugins import openai, noise_cancellation
from openai.types import realtime
from livekit.plugins.openai.realtime import RealtimeModel
import logging
# from agent_instruction import detect_demo_intent,publish_screen_share_lk

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)

# Suppress verbose PIL debug messages
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.getLogger('PIL.PngImagePlugin').setLevel(logging.WARNING)
logging.getLogger('PIL.Image').setLevel(logging.WARNING)


# Configuration
DEMO_PORT = 5000

ROOM_NAME = "product-demo-room"
RTMP_PORT = 1935
# Socket.IO server for signaling
sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp')
app = web.Application()
sio.attach(app)

viewers = {}
BASE_URL=Path(__file__).parent







MEETING_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Product Demo - Live Meeting</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0b0d;
            overflow: hidden;
            height: 100vh;
        }

        /* Email Entry Page */
        .email-entry-page {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            transition: opacity 0.5s ease;
        }
        .email-entry-page.hidden {
            opacity: 0;
            pointer-events: none;
        }
        .email-card {
            background: white;
            border-radius: 20px;
            padding: 50px 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 450px;
            width: 90%;
            text-align: center;
        }
        .email-card h1 {
            color: #1a1d21;
            font-size: 2em;
            margin-bottom: 10px;
        }
        .email-card p {
            color: #8b8d94;
            margin-bottom: 30px;
            font-size: 1.05em;
        }
        .input-group {
            margin-bottom: 25px;
            text-align: left;
        }
        .input-group label {
            display: block;
            color: #1a1d21;
            font-weight: 500;
            margin-bottom: 8px;
            font-size: 0.95em;
        }
        .input-group input {
            width: 100%;
            padding: 14px 18px;
            border: 2px solid #e4e6eb;
            border-radius: 10px;
            font-size: 1em;
            transition: all 0.3s;
            outline: none;
        }
        .input-group input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .input-group input.error {
            border-color: #ff4444;
        }
        .error-message {
            color: #ff4444;
            font-size: 0.85em;
            margin-top: 6px;
            display: none;
        }
        .error-message.show {
            display: block;
        }
        .join-btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .join-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        .join-btn:active {
            transform: translateY(0);
        }

        /* Pre-Meeting Loader */
        .pre-meeting-loader {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #0a0b0d 0%, #1a1d21 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            transition: opacity 0.5s ease;
        }
        .pre-meeting-loader.hidden {
            opacity: 0;
            pointer-events: none;
        }
        .loader-spinner {
            width: 60px;
            height: 60px;
            border: 4px solid rgba(74, 158, 255, 0.1);
            border-top-color: #4a9eff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 25px;
        }
        .loader-text {
            color: #e4e6eb;
            font-size: 1.3em;
            font-weight: 500;
            margin-bottom: 10px;
        }
        .loader-subtitle {
            color: #8b8d94;
            font-size: 0.95em;
        }
        .top-bar {
            height: 60px;
            background: #1a1d21;
            border-bottom: 1px solid #2d3139;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
        }
        .participants-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            background: #2d3139;
            padding: 8px 16px;
            border-radius: 20px;
            color: #e4e6eb;
            font-size: 0.9em;
        }
        .icon-btn {
            width: 36px;
            height: 36px;
            border-radius: 8px;
            background: #2d3139;
            border: none;
            color: #e4e6eb;
            cursor: pointer;
            transition: all 0.2s;
        }
        .icon-btn:hover { background: #3a3f47; }
        .main-container {
            display: flex;
            height: calc(100vh - 140px);
        }
        .video-area {
            flex: 1;
            background: #000;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        #remoteVideo {
            width: 100%;
            height: 100%;
            object-fit: contain;
            background: #000;
        }
        .loading-state {
            position: absolute;
            color: white;
            text-align: center;
            z-index: 10;
        }
        .spinner {
            width: 50px;
            height: 50px;
            border: 3px solid rgba(255,255,255,0.1);
            border-top-color: #4a9eff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .video-overlay {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(10px);
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .live-indicator {
            width: 8px;
            height: 8px;
            background: #ff4444;
            border-radius: 50%;
            animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
        .sidebar {
            width: 360px;
            background: #1a1d21;
            border-left: 1px solid #2d3139;
            display: flex;
            flex-direction: column;
        }
        .sidebar-tabs {
            display: flex;
            border-bottom: 1px solid #2d3139;
        }
        .sidebar-tab {
            flex: 1;
            padding: 15px;
            background: none;
            border: none;
            color: #8b8d94;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s;
            border-bottom: 2px solid transparent;
        }
        .sidebar-tab.active {
            color: #4a9eff;
            border-bottom-color: #4a9eff;
        }
        .sidebar-content {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        .tab-panel { display: none; }
        .tab-panel.active { display: block; }
        .participant-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            background: #2d3139;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .participant-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
        }
        .participant-name {
            color: #e4e6eb;
            font-weight: 500;
        }
        .participant-status {
            color: #8b8d94;
            font-size: 0.8em;
        }
        .chat-message {
            margin-bottom: 16px;
        }
        .message-author {
            color: #4a9eff;
            font-weight: 600;
            font-size: 0.85em;
        }
        .message-time {
            color: #8b8d94;
            font-size: 0.75em;
            margin-left: 8px;
        }
        .message-content {
            background: #2d3139;
            padding: 10px 14px;
            border-radius: 8px;
            color: #e4e6eb;
            margin-top: 6px;
        }
        .system-message {
            text-align: center;
            color: #8b8d94;
            font-size: 0.8em;
            margin: 12px 0;
            font-style: italic;
        }
        .message-author {
            color: #4a9eff;
            font-weight: 600;
            font-size: 0.85em;
        }
        .message-time {
            color: #8b8d94;
            font-size: 0.75em;
            margin-left: 8px;
        }
        .message-content {
            background: #2d3139;
            padding: 10px 14px;
            border-radius: 8px;
            color: #e4e6eb;
            margin-top: 6px;
        }
        .message-content a {
            color: #4a9eff;
            text-decoration: none;
            word-break: break-all;
        }
        .message-content a:hover {
            text-decoration: underline;
        }
        .chat-input-container {
            padding: 15px 20px;
            border-top: 1px solid #2d3139;
        }
        .chat-input-wrapper {
            display: flex;
            gap: 10px;
            background: #2d3139;
            border-radius: 20px;
            padding: 8px 16px;
        }
        #chatInput {
            flex: 1;
            background: none;
            border: none;
            outline: none;
            color: #e4e6eb;
        }
        .send-btn {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: #4a9eff;
            border: none;
            color: white;
            cursor: pointer;
        }
        .bottom-bar {
            height: 80px;
            background: #1a1d21;
            border-top: 1px solid #2d3139;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }
        .control-button {
            width: 52px;
            height: 52px;
            border-radius: 50%;
            border: none;
            background: white;
            color: #e4e6eb;
            cursor: pointer;
            font-size: 1.4em;
            transition: all 0.2s;
            position: relative;
        }
        .control-button:hover {
            background: #3a3f47;
            transform: scale(1.05);
        }
        .control-button.active { background: #4a9eff; }
        .control-button.danger { background: black; }
        .control-label {
            position: absolute;
            bottom: -25px;
            font-size: 0.7em;
            color: #8b8d94;
        }
        .hidden { display: none !important; }
        .error-text { color: #ff4444; }
        .success-text { color: #4ade80; }
    </style>
</head>
<body>
    <!-- Email Entry Page -->
    <div class="email-entry-page" id="emailEntryPage">
        <div class="email-card">
            <h1>Join Meeting</h1>
            <p>Enter your email to join the product demo</p>
            <form id="emailForm" onsubmit="handleEmailSubmit(event)">
                <div class="input-group">
                    <label for="emailInput">Email Address</label>
                    <input 
                        type="email" 
                        id="emailInput" 
                        placeholder="you@example.com" 
                        required
                        autocomplete="email"
                    />
                    <div class="error-message" id="emailError">Please enter a valid email address</div>
                </div>
                <button id="joinBtn" type="submit" class="join-btn">Join Meeting →</button>
            </form>
        </div>
    </div>
    
    <!-- Loading Spinner Page -->
    <div class="pre-meeting-loader" id="preMeetingLoader">
        <div class="loader-spinner"></div>
        <div class="loader-text">Preparing your meeting...</div>
        <div class="loader-subtitle">Connecting you in a moment</div>
    </div>
    
    <!-- Meeting Interface -->
    <div class="meeting-interface" id="meetingInterface">
        <div class="top-bar">
            <div class="participants-badge">
                <span>👥</span>
                <span id="participantCount">Connecting...</span>
            </div>
            <div style="display: flex; gap: 10px;">
                <button class="icon-btn" onclick="toggleFullscreen()">⛶</button>
            </div>
        </div>
        
        <div class="main-container">
            <div class="video-area">
                <div class="loading-state" id="loadingState">
                    <div class="spinner"></div>
                    <div id="statusText">Initializing LiveKit...</div>
                </div>
                <video id="remoteVideo" autoplay playsinline muted></video>
                <audio id="remoteAudio" autoplay playsinline></audio>
                <div class="video-overlay">
                    <div class="live-indicator"></div>
                    <span>Product Demo - LIVE</span>
                </div>
                <div class="mic-status" id="micStatus">
                    <div class="mic-indicator" id="micIndicator"></div>
                    <span id="micText">Microphone Active</span>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="sidebar-tabs">
                    <button class="sidebar-tab active" onclick="switchTab('people')">People</button>
                    <button class="sidebar-tab" onclick="switchTab('chat')">Chat</button>
                </div>
                
                <div class="sidebar-content">
                    <div class="tab-panel active" id="peoplePanel">
                        <div id="participantList">
                            <div class="participant-item">
                                <div class="participant-avatar">🎬</div>
                                <div>
                                    <div class="participant-name">Oncreate Demo Agent</div>
                                    <div class="participant-status">Presenting</div>
                                </div>
                            </div>
                            <div class="participant-item" >
                                <div>
                                    <div class="participant-name">Guest</div>
                                    <div class="participant-status">Attending</div>
                                </div>
                            </div>
                        </div>
                        
                    </div>
                    
                    <div class="tab-panel" id="chatPanel">
                        <div id="chatMessages">
                            <div class="system-message">Welcome! 👋</div>
                            <div class="chat-message">
                            <div>
                                <span class="message-author">Demo Agent</span>
                                <span class="message-time">Now</span>
                            </div>
                                <div class="message-content">
                                    Schedule a follow-up meeting: <a href="https://calendly.com/oncreate/30min?month=2026-01" target="_blank">https://calendly.com/oncreate/30min?month=2026-01</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="chat-input-container">
                    <div class="chat-input-wrapper">
                        <input id="chatInput" placeholder="Send a message..." />
                        <button class="send-btn" onclick="sendMessage()">➤</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="bottom-bar">
            <button class="control-button" id="muteBtn" onclick="toggleMute()">
                <svg xmlns="http://www.w3.org/2000/svg" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd" viewBox="0 0 512 511.999"><path d="M256.001 0C396.8 0 512 115.2 512 256c0 140.799-115.2 255.999-255.999 255.999C115.201 511.999 0 396.799 0 256 0 115.2 115.201 0 256.001 0zm39.23 174.377v65.437c0 56.175-78.463 56.175-78.463 0v-65.437c0-57.755 78.463-57.755 78.463 0zm-29.492 157.905v39.046c0 12.813-19.474 12.813-19.474 0v-39.046a84.378 84.378 0 01-25.903-7.296 85.791 85.791 0 01-24.599-17.195l-.167-.179c-7.808-7.839-14.106-17.182-18.405-27.519a84.508 84.508 0 01-6.494-32.537 9.682 9.682 0 012.867-6.873 9.652 9.652 0 016.873-2.861 9.73 9.73 0 016.885 2.855l.19.212a9.69 9.69 0 012.665 6.667c0 8.876 1.78 17.351 4.994 25.082a66.571 66.571 0 0014.344 21.402c6.097 6.085 13.361 10.999 21.402 14.344a65.134 65.134 0 0025.083 5 65.14 65.14 0 0025.087-5 66.257 66.257 0 0021.391-14.35l.169-.151a66.558 66.558 0 0014.186-21.245 65.204 65.204 0 004.995-25.082 9.714 9.714 0 012.856-6.884 9.724 9.724 0 016.883-2.85c2.682 0 5.12 1.09 6.884 2.85l.196.217a9.704 9.704 0 012.654 6.667 84.658 84.658 0 01-6.482 32.547 85.773 85.773 0 01-18.556 27.711l-.185.167a85.95 85.95 0 01-24.425 17.015 84.696 84.696 0 01-25.914 7.286z"/></svg>
                <span class="control-label">Mute</span>
            </button>
            <button class="control-button" onclick="toggleChat()">
                <svg xmlns="http://www.w3.org/2000/svg" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd" viewBox="0 0 512 452.387"><path fill-rule="nonzero" d="M276.915 436.666c-32.989-9.896-62.965-28.911-87.618-55.815 6.175.567 12.783.958 19.819 1.159 32.31.949 63.167-3.3 91.339-11.815 29.561-8.937 56.687-22.776 79.927-40.41 23.979-18.196 43.56-40.301 57.238-65.17 12.232-22.234 19.84-46.769 21.81-72.836a195.403 195.403 0 0112.994 13.486c19.513 22.316 33.012 48.301 37.715 75.028 4.856 27.594.457 55.851-16.114 81.723-5.048 7.88-11.248 15.52-18.686 22.824l8.165 49.068a15.502 15.502 0 01-.8 8.562c-3.132 8.017-12.171 11.976-20.188 8.844l-55.504-21.826c-44.846 17.676-89.637 19.315-130.097 7.178z"/><path fill="#D8F0F0" d="M212.522 382.09c51.415 47.307 122.9 61.072 194.383 30.61l61.283 24.098-9.593-57.651c57.022-49.859 43.787-119.134-1.727-167.884-3.555 18.854-10.111 36.745-19.248 53.352-13.678 24.869-33.259 46.974-57.238 65.17-23.24 17.634-50.366 31.473-79.927 40.41-27.181 8.215-56.861 12.459-87.933 11.895z"/><path fill-rule="nonzero" d="M369.951 55.167c38.685 33.165 61.879 78.348 60.427 127.704l-.004.172c-1.516 49.407-27.413 93.189-68.065 124.036-39.713 30.136-93.646 47.911-152.383 46.183-15.058-.442-29.669-1.977-43.59-4.684-11.877-2.308-23.389-5.475-34.399-9.545L25.552 371.527l31.949-75.984c-17.241-15.38-31.223-33.198-41.066-52.706C5.175 220.521-.707 196.009.068 170.392 1.561 120.96 27.462 77.156 68.131 46.297c85.638-64.984 220.168-61.131 301.82 8.87z"/><path fill="#91DDAC" d="M220.09 15.665c110.235 3.244 197.422 77.965 194.731 166.89-2.688 88.93-94.233 158.397-204.469 155.154-27.75-.815-54.238-5.665-77.796-15.126l-79.801 24.374 23.518-55.933c-38.601-30.58-62.068-73.422-60.651-120.205 2.685-88.93 94.233-158.395 204.468-155.154z"/><path fill-rule="nonzero" d="M129.631 216.936c-5.368 0-9.72-4.352-9.72-9.72s4.352-9.72 9.72-9.72H249.43c5.368 0 9.72 4.352 9.72 9.72s-4.352 9.72-9.72 9.72H129.631zm0-68.927c-5.368 0-9.72-4.352-9.72-9.72 0-5.367 4.352-9.719 9.72-9.719h171.178c5.368 0 9.719 4.352 9.719 9.719 0 5.368-4.351 9.72-9.719 9.72H129.631z"/></svg>
                <span class="control-label">Chat</span>
            </button>
            <button class="control-button danger" onclick="leaveMeeting()">
                <svg id="Layer_1" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 122.88 122.88"><defs><style>.cls-1{fill:#ff3b30;fill-rule:evenodd;}</style></defs><title>end-call</title><path class="cls-1" d="M104.89,104.89a61.47,61.47,0,1,1,18-43.45,61.21,61.21,0,0,1-18,43.45ZM74.59,55.72a49.79,49.79,0,0,0-12.38-2.07A41.52,41.52,0,0,0,48,55.8a1.16,1.16,0,0,0-.74.67,4.53,4.53,0,0,0-.27,1.7,16.14,16.14,0,0,0,.2,2c.42,3,.93,6.8-2.42,8l-.22.07-12,3.24-.12,0A4.85,4.85,0,0,1,28,70a11.44,11.44,0,0,1-2.68-4.92,11,11,0,0,1,.42-6.93A23.69,23.69,0,0,1,29,52.39,21.52,21.52,0,0,1,36.55,46a42.74,42.74,0,0,1,10.33-3.6l.29-.07C49,42,51,41.48,53.08,41.17a62.76,62.76,0,0,1,25.14,1.59c6.87,2,13,5.43,16.8,10.7a13.88,13.88,0,0,1,2.92,9.59,12.64,12.64,0,0,1-4.88,8.43,1.34,1.34,0,0,1-1.26.28L78.6,68.38A3.69,3.69,0,0,1,75.41,66a7.73,7.73,0,0,1-.22-4,15.21,15.21,0,0,1,.22-1.6c.3-1.89.63-4.06-.89-4.72Z"/></svg>
                <span class="control-label">Leave</span>
            </button>
        </div>
    </div>

    <script type="module">
        import * as LivekitClient from 'https://cdn.jsdelivr.net/npm/livekit-client@2.5.8/dist/livekit-client.esm.mjs';
        
        window.LivekitClient = LivekitClient;
        
        let room = null;
        let userEmail = '';
        let userName = '';
        let sessionId = null;
        let localAudioTrack = null;
        let isMuted = false;
        let audioContext = null;
        let audioDestination = null;
        
        window.handleEmailSubmit = async function(event) {
            event.preventDefault();
            
            const emailInput = document.getElementById('emailInput');
            const joinBtn = document.getElementById('joinBtn');
            const email = emailInput.value.trim();
            
            joinBtn.disabled = true;
            joinBtn.textContent = 'Joining...';
            
            try {
                userEmail = email;
                userName = email.split('@')[0];
                
                const response = await fetch('/user-joined', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: userEmail, session_id: sessionId })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    sessionId = data.session_id;
                    console.log('✅ Session ID:', sessionId);
                    
                    document.getElementById('emailEntryPage').classList.add('hidden');
                    document.getElementById('preMeetingLoader').classList.remove('hidden');
                    
                    setTimeout(() => connectToRoom(), 500);
                } else {
                    throw new Error('Failed to join');
                }
            } catch (error) {
                console.error('Join error:', error);
                alert('Failed to join. Please try again.');
                joinBtn.disabled = false;
                joinBtn.textContent = 'Join Meeting →';
            }
        }
        
        function updateStatus(message) {
            document.getElementById('statusText').textContent = message;
            console.log(message);
        }
        
        async function connectToRoom() {
            try {
                updateStatus('Getting token...');
                
                const tokenResp = await fetch(`/token?name=${encodeURIComponent(userName)}&session_id=${sessionId}`);
                if (!tokenResp.ok) throw new Error('Token fetch failed');
                
                const {token} = await tokenResp.json();
                console.log('✅ Token received');
                
                updateStatus('Requesting microphone...');
                
                // Initialize audio context
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                audioDestination = audioContext.createMediaStreamDestination();
                
                // Get microphone
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    } 
                });
                
                console.log('✅ Microphone granted');
                
                // Create audio track
                const audioTrack = stream.getAudioTracks()[0];
                localAudioTrack = new LivekitClient.LocalAudioTrack(audioTrack);
                
                updateStatus('Connecting to room...');
                
                // Create room
                room = new LivekitClient.Room({
                    adaptiveStream: true,
                    dynacast: true,
                });
                
                // Event handlers
                room.on(LivekitClient.RoomEvent.TrackSubscribed, handleTrackSubscribed);
                room.on(LivekitClient.RoomEvent.TrackUnsubscribed, handleTrackUnsubscribed);
                room.on(LivekitClient.RoomEvent.ParticipantConnected, handleParticipantConnected);
                room.on(LivekitClient.RoomEvent.Disconnected, handleDisconnected);
                room.on(LivekitClient.RoomEvent.DataReceived, handleDataReceived);
                
                // Connect
                await room.connect('{{ LIVEKIT_URL }}', token);
                console.log('✅ Connected to room');
                
                // Publish microphone
                await room.localParticipant.publishTrack(localAudioTrack);
                console.log('✅ Microphone published');
                
                updateMicStatus(false);
                updateParticipants();
                
                document.getElementById('preMeetingLoader').classList.add('hidden');
                document.getElementById('meetingInterface').classList.remove('hidden');
                
                updateStatus('Connecting to the Room.....');
                
            } catch (error) {
                console.error('❌ Connection error:', error);
                updateStatus('Failed: ' + error.message);
                alert('Connection failed: ' + error.message);
            }
        }
        
        function handleTrackSubscribed(track, publication, participant) {
            console.log('📹 Track subscribed:', track.kind, 'from', participant.identity);
            
            if (track.kind === LivekitClient.Track.Kind.Video) {
                const videoEl = document.getElementById('remoteVideo');
                track.attach(videoEl);
                document.getElementById('loadingState').classList.add('hidden');
                console.log('✅ Video attached');
            } 
            else if (track.kind === LivekitClient.Track.Kind.Audio) {
                // Create audio element dynamically
                const audioEl = document.createElement('audio');
                audioEl.autoplay = true;
                audioEl.playsInline = true;
                audioEl.id = 'agent-audio-' + participant.identity;
                document.body.appendChild(audioEl);
                
                track.attach(audioEl);
                
                // Ensure playback
                audioEl.play().then(() => {
                    console.log('✅ Agent audio playing in browser');
                }).catch(err => {
                    console.error('Audio play error:', err);
                    // Try user interaction
                    document.addEventListener('click', () => {
                        audioEl.play();
                    }, { once: true });
                });
            }
        }
        
        function handleTrackUnsubscribed(track, publication, participant) {
            console.log('Track unsubscribed:', track.kind);
            const audioEl = document.getElementById('agent-audio-' + participant.identity);
            if (audioEl) {
                track.detach(audioEl);
                audioEl.remove();
            }
        }
        
        function handleParticipantConnected(participant) {
            console.log('👤 Participant joined:', participant.identity);
            updateParticipants();
        }
        
        function handleDisconnected() {
            console.log('❌ Disconnected');
            updateStatus('Disconnected');
        }
        
        function handleDataReceived(payload, participant) {
            const decoder = new TextDecoder();
            const message = JSON.parse(decoder.decode(payload));
            if (message.type === 'chat') {
                addChatMessage(participant.identity, message.text);
            }
        }
        
        function updateParticipants() {
            if (!room) return;
            const count = room.remoteParticipants.size + 1;
            document.getElementById('participantCount').textContent = count + ' in call';
        }
        
        function updateMicStatus(muted) {
            // Try legacy/expected ids first, fall back to the mic indicator/text present
            const wave = document.getElementById('audioWave') || document.getElementById('micIndicator');
            const status = document.getElementById('audioStatus') || document.getElementById('micText');
            const btn = document.getElementById('muteBtn');

            // Safely update visual indicator (if present)
            if (wave) {
                if (muted) {
                    wave.classList.add('muted');
                } else {
                    wave.classList.remove('muted');
                }
            }

            // Safely update status text (if present)
            if (status) {
                status.textContent = muted ? 'Mic Muted' : 'Mic Active';
            }

            // Safely toggle button active state (if present)
            if (btn) {
                if (muted) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            }
        }
        
        window.toggleMute = async function() {
            if (!localAudioTrack) return;
            
            isMuted = !isMuted;
            
            if (isMuted) {
                await localAudioTrack.mute();
                console.log('🔇 Muted');
            } else {
                await localAudioTrack.unmute();
                console.log('🔊 Unmuted');
            }
            
            updateMicStatus(isMuted);
        }
        
        window.leaveMeeting = async function() {
            if (confirm('Leave meeting?')) {
                if (sessionId) {
                    fetch('/user-left', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ session_id: sessionId })
                    }).catch(console.error);
                }
                
                if (localAudioTrack) {
                    localAudioTrack.stop();
                }
                
                if (room) {
                    room.disconnect();
                }
                
                location.reload();
            }
        }
        
        window.switchTab = function(tab) {
            document.querySelectorAll('.sidebar-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tab + 'Panel').classList.add('active');
        }
        
        function addChatMessage(author, text) {
            const chatDiv = document.getElementById('chatMessages');
            const msg = document.createElement('div');
            msg.className = 'chat-message';
            msg.innerHTML = `
                <div><span class="message-author">${escapeHtml(author)}</span></div>
                <div class="message-content">${escapeHtml(text)}</div>
            `;
            chatDiv.appendChild(msg);
            chatDiv.scrollTop = chatDiv.scrollHeight;
        }
        
        window.sendMessage = function() {
            const input = document.getElementById('chatInput');
            const text = input.value.trim();
            if (!text || !room) return;
            
            const data = { type: 'chat', text };
            const encoder = new TextEncoder();
            const encoded = encoder.encode(JSON.stringify(data));
            
            room.localParticipant.publishData(encoded, LivekitClient.DataPacket_Kind.RELIABLE);
            addChatMessage(userName + ' (You)', text);
            input.value = '';
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        
        window.addEventListener('beforeunload', () => {
            if (sessionId) {
                navigator.sendBeacon('/user-left', 
                    new Blob([JSON.stringify({ session_id: sessionId })], 
                    { type: 'application/json' }));
            }
        });
        
    </script>
</body>
</html>
"""

ONCREATE_URL = "http://agent.oncreate.ai/app.html"
# Generate LiveKit token
def create_token(room_name: str, participant_name: str) -> str:
    token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    token.with_identity(participant_name)
    token.with_name(participant_name)
    token.with_grants(api.VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True,
    ))
    return token.to_jwt()

# HTTP routes
async def meeting_page(request):
    html = MEETING_HTML.replace('{{ LIVEKIT_URL }}', LIVEKIT_URL)
    return web.Response(text=html, content_type='text/html')

async def get_token(request):
    name = request.query.get('name', f'Guest_{os.urandom(4).hex()}')
    token = create_token(ROOM_NAME, name)
    return web.json_response({'token': token})

active_sessions = {}
session_lock = asyncio.Lock()
random = os.urandom(8).hex()
user_join_queue = asyncio.Queue()

# Add a new endpoint to signal when user joins
async def user_joined(request):
    """Called when user submits email and joins meeting"""
    try:
        data = await request.json()
        user_email = data.get('email')
        session_id = data.get('session_id') or random
        
       
            # Signal that this session should start initialization
        active_sessions[session_id] = {
            'email': user_email,
            'status': 'active',
            'timestamp': asyncio.get_event_loop().time()
        }
            
        print(f"👤 User joined: {user_email} (session: {session_id})")
        
        # Trigger the initialization for this session
        # active_sessions[session_id]['ready'].set()

        await user_join_queue.put({'session_id': session_id,
                                     'email': user_email,
                                     })


        
        return web.json_response({
            'success': True,
            'session_id': session_id
        })
    except Exception as e:
        print(f"Error in user_joined: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)
    
async def user_left(request):
    """Called when user leaves the meeting"""
    try:
        data = await request.json()
        session_id = data.get('session_id')
        
        async with session_lock:
            if session_id in active_sessions:
                active_sessions[session_id]['status'] = 'left'
                print(f"👋 User left session: {session_id}")
        
        return web.json_response({'success': True})
    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)}, status=500)


app.router.add_get('/', meeting_page)
app.router.add_get('/token', get_token)
app.router.add_post('/user-joined', user_joined)
app.router.add_post('/user-left', user_left)


async def start_server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', DEMO_PORT)
    await site.start()
    print(f" Meeting server: http://localhost:{DEMO_PORT}")









conversation_state = {
    "stage": "greeting",
    "user_name": None,
    "company_product": None,
    "demo_started": False,
}
server = AgentServer()

@server.rtc_session()
async def entrypoint(ctx: JobContext):

    """Main entry point for the LiveKit agent"""
    
    print(f"🎤 Starting agent in room: {ctx.room.name}")
    
    # Connect to room
    
    await ctx.connect()
    print("✅ Connected to Voice LiveKit")
    await start_server()

    while True:
        
        
        # session_id = random
        # Wait for user to submit email and join
        print("⏳ Waiting for user to submit email...")
        user_info = await user_join_queue.get()
        
        session_id = user_info['session_id']
        user_email = user_info['email']
        
        # Wait for the ready event (triggered when user submits email)
        print(f"✅ User {user_email} joined! Starting initialization for session {session_id}...")
        print("User joined, proceeding with agent...")
        # Add logging in your entrypoint:
        print(f"Agent tracks: {ctx.room.local_participant.track_publications}")
        
        playwright = None
        browser = None
        room_obj = None
        
        # Launch Playwright
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=True,
            slow_mo=2000,
            args=[
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-setuid-sandbox',
                '--no-sandbox',
            ]
        )
        context = await browser.new_context()
        page = await context.new_page()
        
        print("🌐 Navigating to demo page...")
        await page.goto(ONCREATE_URL, wait_until="domcontentloaded")

        await inject_cursor_styles(page)
        await set_cursor_mode(page, mode="pointer")
        await click_with_cursor(page, 'button[data-title="Agents"]')
        
        print("🔌 Connecting to LiveKit room...")
        room_obj = rtc.Room()
        
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.with_identity("Demo-Agent")
        token.with_name("Demo Agent")
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=ROOM_NAME,
            can_publish=True,
            can_subscribe=True,
        ))
        jwt_token = token.to_jwt()
        
        await room_obj.connect(LIVEKIT_URL, jwt_token)
        print("✅ Connected to LiveKit room")

        async def publish_screen_share(room: rtc.Room, page):
            """Capture Playwright screenshots and publish to LiveKit"""
            
            # await asyncio.sleep(1)
            
            # Get dimensions
            png = await page.screenshot(type='png', timeout=60000)
            img = Image.open(io.BytesIO(png)).convert('RGB')
            width, height = img.size
            
            print(f"📺 Screen: {width}x{height}")
            
            # Create video source
            video_src = rtc.VideoSource(width, height)
            local_track = rtc.LocalVideoTrack.create_video_track("screen-share", video_src)
            
            # Publish track
            await room.local_participant.publish_track(
                local_track,
                rtc.TrackPublishOptions(
                    source=rtc.TrackSource.SOURCE_SCREENSHARE,
                    video_encoding=rtc.VideoEncoding(
                        max_bitrate=3_000_000,
                        max_framerate=15.0,
                    )
                )
            )
            
            print("✅ Screen share started")
            
            # Capture loop
            fps = 15
            frame_interval = 1.0 / fps
            
            try:
                while True:
                    start_time = time.time()
                    
                    png = await page.screenshot(type='png', timeout=60000)
                    img = Image.open(io.BytesIO(png)).convert('RGB')
                    
                    if img.size != (width, height):
                        img = img.resize((width, height), Image.BILINEAR)
                    
                    buf = img.tobytes()
                    vf = rtc.VideoFrame(width, height, rtc.VideoBufferType.RGB24, buf)
                    timestamp_us = int(time.time() * 1_000_000)
                    video_src.capture_frame(vf, timestamp_us=timestamp_us)

                    
                    
                    elapsed = time.time() - start_time
                    await asyncio.sleep(max(0, frame_interval - elapsed))
                    
            except asyncio.CancelledError:
                print("🛑 Screen capture stopped")

            except Exception as ex:
                logging.error(f"Screen Capture Error:{ex}")

                

        screen_task = asyncio.create_task(publish_screen_share(room_obj, page))

        # Create agent
        agent = DemoAgent()

        model=RealtimeModel(
            voice="ash",
            modalities=["text","audio"],
            input_audio_transcription=realtime.AudioTranscription(
                model="gpt-4o-transcribe"
            ),
            input_audio_noise_reduction="near_field",
            turn_detection=realtime.realtime_audio_input_turn_detection.SemanticVad(
                type="semantic_vad",
                create_response=True,
                eagerness="auto",
                interrupt_response=True,
            ),
            )

        session= AgentSession(llm=model)
        
        print("🤖 Starting session...")

        await session.start(
                    room=room_obj,
                    agent=agent,
                    room_options=room_io.RoomOptions(
                        audio_input=room_io.AudioInputOptions(
                            noise_cancellation=lambda params: noise_cancellation.BVC()
                        ),
                    )
                    )

        async def _print_transcript_async(ev):
            try:
                txt = getattr(ev, "transcript", "") or ""
                is_final = getattr(ev, "is_final", False)
                tag = "(final)" if is_final else ""
                logger.info(f"📝 Transcript User: {txt}")

                if  is_demo_intent(txt):
                    logger.info("Starting the demo")
                    asyncio.create_task(run(page=page, browser=browser, session=session))

                # Example async work you might want to run per-transcript:
                # await some_async_function(ev)
            except Exception:
                logger.exception("error printing transcript")

        def _print_transcript(ev):
            try:
                asyncio.create_task(_print_transcript_async(ev))
            except Exception:
                logger.exception("failed scheduling transcript task")

        session.on("user_input_transcribed", _print_transcript)
        
        print("✅ Agent ready")
        

        
        # Monitor conversation
        async def monitor_conversation():

            # import pdb; pdb.set_trace()
            
            last_stage = conversation_state["stage"]
            logger.info("Starting conversation monitor")
            if conversation_state["stage"] == "greeting":
                logger.info("Greeting from the agent")
                await asyncio.sleep(1)
                await session.generate_reply(instructions=agent.get_current_instructions(stage="greeting"))
                await asyncio.sleep(3)
                
        
        
        monitor_task=asyncio.create_task(monitor_conversation())

        while active_sessions.get(session_id, {}).get('status') != 'left':
                await asyncio.sleep(1)
        logger.info(f"🛑 User left, shutting down session {session_id}...")  
        # await session.aclose()

        # Cancel and await background tasks to ensure they stop cleanly
        for t in (screen_task, monitor_task):
            if t:
                t.cancel()
                try:
                    await t
                except asyncio.CancelledError:
                    pass
                except Exception:
                    logger.exception("Error awaiting cancelled task")

        # Ensure audio queues/buffers are cleared so next session can start cleanly

        await room_obj.disconnect()
        await ctx.room.disconnect()
        session = None
        model = None
        # ctx.room = None
        
            # Cleanup
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()

        
        del active_sessions[session_id]
        # ctx.shutdown()
        



if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint,api_key=LIVEKIT_API_KEY,api_secret=LIVEKIT_API_SECRET,ws_url=LIVEKIT_URL))