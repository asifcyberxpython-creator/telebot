# File: telegram/bot/services/tunnel_service.py
import subprocess
import re
import time
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from threading import Thread, Event
import logging

logger = logging.getLogger(__name__)

def get_cloudflared_path() -> str:
    """
    Find the cloudflared executable path.
    1. Check system PATH first.
    2. Check 'bin/' directory in the project root.
    3. If not found, download it automatically to the local 'bin/' folder!
    """
    system_path = shutil.which("cloudflared")
    if system_path:
        return system_path
        
    project_root = Path(__file__).resolve().parent.parent.parent
    local_bin_dir = project_root / "bin"
    exe_name = "cloudflared.exe" if sys.platform == "win32" else "cloudflared"
    local_path = local_bin_dir / exe_name
    
    if local_path.exists():
        return str(local_path)
        
    # Attempt automatic download
    try:
        logger.info("cloudflared binary not found. Attempting to download it automatically...")
        local_bin_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine download URL
        if sys.platform == "win32":
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        elif sys.platform == "darwin":
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64"
        else:
            # Assume Linux
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
            
        logger.info(f"Downloading cloudflared from {url}...")
        
        import requests
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        # Make executable on Unix/Mac
        if sys.platform != "win32":
            os.chmod(local_path, 0o755)
            
        logger.info(f"cloudflared downloaded successfully to {local_path}")
        return str(local_path)
        
    except Exception as e:
        logger.error(f"Failed to automatically download cloudflared: {e}")
        return "cloudflared"

class CloudflareTunnelService:
    def __init__(self):
        self.tunnel_process = None
        self.process_running = False
        self.url_pattern = r'https://(?!api\.)[a-z0-9\-]+\.trycloudflare\.com'
        self.start_time = None
        self.local_port = 8080
        self.current_tunnel_url = None
        self.masked_url = None
        self.stop_event = Event()
        
    def start_tunnel(self, local_port: int = 8080) -> bool:
        """Start Cloudflare tunnel for specified port"""
        if self.process_running:
            return False
            
        try:
            self.local_port = local_port
            self.start_time = datetime.now()
            
            # Combine stderr into stdout since cloudflared logs primarily to stderr
            # Force HTTP2 protocol to bypass firewalls blocking UDP/7844 (QUIC)
            self.tunnel_process = subprocess.Popen(
                [get_cloudflared_path(), "tunnel", "--protocol", "http2", "--url", f"http://localhost:{local_port}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            self.process_running = True
            self.stop_event.clear()
            self.current_tunnel_url = None
            self.masked_url = None
            
            # Monitor output in a separate thread
            Thread(target=self._monitor_output, daemon=True).start()
            return True
            
        except FileNotFoundError:
            logger.error("cloudflared binary not found. Please install Cloudflare Tunnel.")
            raise Exception("cloudflared binary not found. Please install Cloudflare Tunnel.")
        except Exception as e:
            self.process_running = False
            logger.error(f"Tunnel start failed: {str(e)}")
            raise Exception(f"Tunnel start failed: {str(e)}")
    
    def _monitor_output(self):
        """Monitor tunnel process output to extract URL"""
        try:
            while self.process_running and not self.stop_event.is_set():
                line = self.tunnel_process.stdout.readline()
                if not line:
                    break
                url_match = re.search(self.url_pattern, line)
                if url_match and not self.current_tunnel_url:
                    self.current_tunnel_url = url_match.group(0)
                    logger.info(f"Cloudflare tunnel URL detected: {self.current_tunnel_url}")
        except Exception as e:
            logger.error(f"Error monitoring tunnel output: {str(e)}")
    
    def stop_tunnel(self):
        """Stop the Cloudflare tunnel"""
        if not self.process_running:
            return False
            
        try:
            self.stop_event.set()
            if self.tunnel_process:
                self.tunnel_process.terminate()
                self.tunnel_process.wait(timeout=5)
            self.process_running = False
            self.current_tunnel_url = None
            self.masked_url = None
            return True
        except Exception as e:
            logger.error(f"Error stopping tunnel: {str(e)}")
            return False
    
    def restart_tunnel(self):
        """Restart the Cloudflare tunnel"""
        if self.process_running:
            self.stop_tunnel()
        return self.start_tunnel(self.local_port)
    
    def get_status(self):
        """Get current tunnel status"""
        if not self.process_running:
            return {
                "running": False,
                "url": None,
                "masked_url": None,
                "start_time": None,
                "duration": None
            }
            
        duration = datetime.now() - self.start_time
        return {
            "running": True,
            "url": self.current_tunnel_url,
            "masked_url": self.masked_url,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration": str(duration).split('.')[0]
        }
    
    def set_masked_url(self, masked_url: str):
        """Store the masked URL for this tunnel"""
        self.masked_url = masked_url
    
    def is_running(self) -> bool:
        """Check if tunnel is running"""
        return self.process_running
    
    def cleanup(self):
        """Clean up resources when shutting down"""
        if self.process_running:
            self.stop_tunnel()