"""
CyberAI Bot — URL Masker Service
Wraps the existing url_masker/main.py functions without modifying the original file.
Imports and uses: validate_url, normalize_url, shorten_url, create_masked_url
"""

import sys
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict
from concurrent.futures import ThreadPoolExecutor

from bot.config import URL_MASKER_DIR

logger = logging.getLogger(__name__)

# Add url_masker directory to path so we can import its functions
_masker_path = str(URL_MASKER_DIR)
if _masker_path not in sys.path:
    sys.path.insert(0, _masker_path)

# Import the core functions from the existing url_masker/main.py
# These are pure functions that don't require terminal interaction
try:
    from url_masker.main import validate_url, normalize_url, create_masked_url, shorten_url as _shorten_url
    logger.info("URL Masker functions imported successfully")
except ImportError:
    # Fallback: define them locally if import path issues
    logger.warning("Could not import from url_masker.main, using local implementations")

    import urllib.parse

    def validate_url(url):
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def normalize_url(url):
        if not url.startswith(('http://', 'https://')):
            return 'https://' + url
        return url

    def create_masked_url(short_url, mask_text, custom_words=''):
        short_domain = short_url.replace('https://', '').replace('http://', '')
        mask_text = mask_text.replace('https://', '').replace('http://', '').strip()
        if custom_words:
            custom_words = custom_words.strip().replace(' ', '-')

        if custom_words:
            masked_url_1 = f"https://{mask_text}-{custom_words}@{short_domain}"
        else:
            masked_url_1 = f"https://{mask_text}@{short_domain}"

        if custom_words:
            masked_url_2 = f"https://{custom_words}.{mask_text}.{short_domain}"
        else:
            masked_url_2 = f"https://{mask_text}.{short_domain}"

        if custom_words:
            masked_url_3 = f"{short_url}/{custom_words}#{mask_text}"
        else:
            masked_url_3 = f"{short_url}#{mask_text}"

        if custom_words:
            masked_url_4 = f"{short_url}?redirect={mask_text}&token={custom_words}"
        else:
            masked_url_4 = f"{short_url}?redirect={mask_text}"

        return {
            'method_1': masked_url_1,
            'method_2': masked_url_2,
            'method_3': masked_url_3,
            'method_4': masked_url_4,
            'original_short': short_url
        }

    def _shorten_url(original_url):
        try:
            import pyshorteners
            s = pyshorteners.Shortener()
            shorteners = [
                ('TinyURL', s.tinyurl),
                ('Dagd', s.dagd),
                ('Clckru', s.clckru),
                ('Osdb', s.osdb),
            ]
            for name, shortener in shorteners:
                try:
                    result = shortener.short(original_url)
                    if result:
                        return result
                except Exception:
                    continue
        except ImportError:
            pass
        return None


# Thread pool for blocking I/O operations (URL shortening)
_executor = ThreadPoolExecutor(max_workers=2)


class MaskerService:
    """
    Provides URL masking functionality for the Telegram bot.
    Wraps the existing url_masker functions.
    """

    @staticmethod
    def validate_and_normalize(url: str) -> tuple:
        """
        Validate and normalize a URL.
        Returns (normalized_url, error_message).
        If valid, error_message is None.
        """
        if not url or not url.strip():
            return None, "No URL provided"

        normalized = normalize_url(url.strip())

        if not validate_url(normalized):
            return None, "Invalid URL format. Please include the protocol (http:// or https://)"

        return normalized, None

    @staticmethod
    async def mask_url(original_url: str, mask_domain: str,
                       custom_words: str = '') -> Dict:
        """
        Mask a URL asynchronously.

        Returns dict with keys:
          - success: bool
          - original_url: str
          - shortened_url: str
          - masked_urls: dict (method_1, method_2, method_3, method_4)
          - error: str (if success is False)
        """
        try:
            # Normalize the original URL
            original_url = normalize_url(original_url.strip())

            if not validate_url(original_url):
                return {
                    "success": False,
                    "error": "Invalid URL format",
                }

            # Shorten URL in a thread pool (blocking I/O)
            loop = asyncio.get_event_loop()
            shortened = await loop.run_in_executor(_executor, _shorten_url, original_url)

            if not shortened:
                # Fallback: use original URL if shortening fails
                logger.warning(f"URL shortening failed for {original_url}, using original")
                shortened = original_url

            # Create masked URLs (this is CPU-only, fast)
            masked = create_masked_url(shortened, mask_domain, custom_words)

            return {
                "success": True,
                "original_url": original_url,
                "shortened_url": shortened,
                "masked_urls": masked,
                "error": None,
            }

        except Exception as e:
            logger.error(f"URL masking error: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def mask_url_sync(original_url: str, mask_domain: str,
                      custom_words: str = '') -> Dict:
        """
        Synchronous version of mask_url for non-async contexts.
        """
        try:
            original_url = normalize_url(original_url.strip())

            if not validate_url(original_url):
                return {"success": False, "error": "Invalid URL format"}

            shortened = _shorten_url(original_url)
            if not shortened:
                shortened = original_url

            masked = create_masked_url(shortened, mask_domain, custom_words)

            return {
                "success": True,
                "original_url": original_url,
                "shortened_url": shortened,
                "masked_urls": masked,
                "error": None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton
masker_service = MaskerService()
