#!/usr/bin/env python3
"""
CyberAI Telegram Bot — Entry Point
Run this file to start the bot: python run.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.main import run

if __name__ == "__main__":
    import sys
    import io
    # Fix Windows console encoding
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    print()
    print("  +==========================================+")
    print("  |       CyberAI Telegram Bot               |")
    print("  |                                          |")
    print("  |   Camera Capture + URL Masker            |")
    print("  |   Unified Telegram Interface             |")
    print("  |                                          |")
    print("  |   Bot: @telecyber_ai_bot                 |")
    print("  +==========================================+")
    print()

    run()
