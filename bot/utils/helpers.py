"""
CyberAI Bot — Utility Helpers
File handling, sanitization, formatting, and general utilities.
"""

import os
import re
import zipfile
import datetime
from pathlib import Path
from typing import List, Optional


def sanitize_filename(filename: str) -> str:
    """Remove or replace characters that are unsafe for filenames."""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip('. ')
    if not filename:
        filename = "unnamed"
    return filename[:200]  # limit length


def format_uptime(start_time: datetime.datetime) -> str:
    """Format elapsed time since start_time as human-readable string."""
    delta = datetime.datetime.now() - start_time
    total_seconds = int(delta.total_seconds())

    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        mins = total_seconds // 60
        secs = total_seconds % 60
        return f"{mins}m {secs}s"
    else:
        hours = total_seconds // 3600
        mins = (total_seconds % 3600) // 60
        return f"{hours}h {mins}m"


def format_file_size(size_bytes: int) -> str:
    """Format file size as human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def zip_directory(dir_path: Path, output_path: Path) -> Optional[Path]:
    """Zip all files in a directory. Returns path to zip file or None if empty."""
    files = list(dir_path.iterdir())
    files = [f for f in files if f.is_file()]

    if not files:
        return None

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            zf.write(file, file.name)

    return output_path


def get_latest_files(dir_path: Path, limit: int = 5, extensions: tuple = ('.png', '.jpg', '.jpeg')) -> List[Path]:
    """Get the latest N files from a directory, sorted by modification time."""
    if not dir_path.exists():
        return []

    files = [
        f for f in dir_path.iterdir()
        if f.is_file() and f.suffix.lower() in extensions
    ]

    # Sort by modification time, newest first
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return files[:limit]


def count_files(dir_path: Path, extensions: tuple = ('.png', '.jpg', '.jpeg')) -> int:
    """Count files in a directory matching given extensions."""
    if not dir_path.exists():
        return 0
    return sum(
        1 for f in dir_path.iterdir()
        if f.is_file() and f.suffix.lower() in extensions
    )


def read_log_file(log_path: Path, tail_lines: int = 50) -> str:
    """Read the last N lines of a log file."""
    if not log_path.exists():
        return ""

    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        if tail_lines and len(lines) > tail_lines:
            lines = lines[-tail_lines:]

        return ''.join(lines)
    except Exception:
        return ""


def count_log_lines(log_path: Path) -> int:
    """Count total lines in a log file."""
    if not log_path.exists():
        return 0
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def clear_directory(dir_path: Path, extensions: tuple = ('.png', '.jpg', '.jpeg')) -> int:
    """Delete all files with given extensions in a directory. Returns count deleted."""
    if not dir_path.exists():
        return 0

    count = 0
    for f in dir_path.iterdir():
        if f.is_file() and f.suffix.lower() in extensions:
            try:
                f.unlink()
                count += 1
            except Exception:
                pass
    return count


def clear_log_file(log_path: Path) -> bool:
    """Clear a log file by truncating it."""
    try:
        if log_path.exists():
            with open(log_path, 'w') as f:
                f.write("")
        return True
    except Exception:
        return False


def truncate_message(text: str, max_length: int = 4096) -> str:
    """Truncate a message to fit within Telegram's character limit."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 20] + "\n\n<i>...truncated</i>"


def get_new_files_since(dir_path: Path, since: datetime.datetime,
                        extensions: tuple = ('.png', '.jpg', '.jpeg')) -> List[Path]:
    """Get files created/modified after a specific timestamp."""
    if not dir_path.exists():
        return []

    since_ts = since.timestamp()
    files = [
        f for f in dir_path.iterdir()
        if f.is_file()
        and f.suffix.lower() in extensions
        and f.stat().st_mtime > since_ts
    ]
    files.sort(key=lambda f: f.stat().st_mtime)
    return files
