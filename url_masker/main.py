
#!/usr/bin/env python3
"""
URL Masker - Terminal-based URL masking tool
Masks a real URL to appear as a custom URL while still redirecting to the original
"""

import sys
import urllib.parse
import requests
import json
import random
import string
import os
import datetime
import time
import threading
import itertools


class Colors:
    """Terminal colors for better UX"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_char_animated(text, delay=0.03):
    """Print text with typing animation"""
    import time
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def print_banner():
    """Display tool banner with animation"""
    import time
    
    banner = f"""{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════╗
║           URL MASKER - Terminal Edition              ║
║         Mask URLs for Social Engineering             ║
║                   Created by: ASIF                   ║
╚══════════════════════════════════════════════════════╝
{Colors.ENDC}"""
    print(banner)
    time.sleep(0.3)


def show_ethical_disclaimer():
    """Show ethical use disclaimer and get confirmation"""
    import time
    
    print(f"\n{Colors.RED}{Colors.BOLD}{'⚠️  ETHICAL USE AGREEMENT  ⚠️':^70}{Colors.ENDC}\n")
    time.sleep(0.2)
    
    disclaimer = [
        f"{Colors.YELLOW}This tool is for AUTHORIZED purposes ONLY:{Colors.ENDC}",
        f"{Colors.CYAN}  • Security awareness training{Colors.ENDC}",
        f"{Colors.CYAN}  • Authorized penetration testing{Colors.ENDC}",
        f"{Colors.CYAN}  • Educational demonstrations{Colors.ENDC}",
        f"{Colors.CYAN}  • Personal ethical projects{Colors.ENDC}",
        "",
        f"{Colors.RED}⛔ Unauthorized use for phishing or malicious activities is ILLEGAL!{Colors.ENDC}",
    ]
    
    for line in disclaimer:
        print(line)
        time.sleep(0.1)
    
    print(f"\n{Colors.BOLD}Do you agree to use this tool ONLY for ethical purposes? (yes/no): {Colors.ENDC}", end='')
    agreement = input().strip().lower()
    
    if agreement not in ['yes', 'y']:
        print(f"\n{Colors.RED}[✗] Agreement required to use this tool. Exiting...{Colors.ENDC}\n")
        sys.exit(0)
    
    print(f"{Colors.GREEN}[✓] Agreement accepted. Proceeding...{Colors.ENDC}\n")
    time.sleep(0.5)


def validate_url(url):
    """Validate if the URL is properly formatted"""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def normalize_url(url):
    """Normalize URL by adding https:// if not present"""
    if not url.startswith(('http://', 'https://')):
        return 'https://' + url
    return url


def loading_animation(duration=2):
    """Show a loading animation"""
    import time
    import itertools
    
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    end_time = time.time() + duration
    
    while time.time() < end_time:
        print(f"\r{Colors.YELLOW}[{next(spinner)}] Processing...{Colors.ENDC}", end='', flush=True)
        time.sleep(0.1)
    print(f"\r{' ' * 50}\r", end='', flush=True)


def shorten_url(original_url):
    """
    Shorten URL using pyshorteners library with multiple fallback services
    """
    import time
    import itertools
    
    try:
        import pyshorteners
    except ImportError:
        print(f"{Colors.RED}[✗] pyshorteners library not found!{Colors.ENDC}")
        print(f"{Colors.YELLOW}[!] Installing pyshorteners...{Colors.ENDC}")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyshorteners"])
        import pyshorteners
    
    # Initialize shorteners
    s = pyshorteners.Shortener()
    
    # List of shorteners to try
    shorteners = [
        ('TinyURL', s.tinyurl),
        ('Dagd', s.dagd),
        ('Clckru', s.clckru),
        ('Osdb', s.osdb),
    ]
    
    for name, shortener in shorteners:
        try:
            print(f"{Colors.YELLOW}[*] Shortening URL with {name}...{Colors.ENDC}")
            
            # Animation
            spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
            
            # Try shortening in background thread
            result = {'url': None, 'done': False, 'error': None}
            
            def fetch_url():
                try:
                    result['url'] = shortener.short(original_url)
                except Exception as e:
                    result['error'] = str(e)
                result['done'] = True
            
            import threading
            thread = threading.Thread(target=fetch_url)
            thread.start()
            
            # Show spinner
            timeout = time.time() + 10
            while not result['done'] and time.time() < timeout:
                print(f"\r{Colors.YELLOW}[{next(spinner)}] Shortening URL with {name}...{Colors.ENDC}", end='', flush=True)
                time.sleep(0.1)
            
            print(f"\r{' ' * 70}\r", end='', flush=True)
            
            if result['url']:
                print(f"{Colors.GREEN}[✓] URL shortened successfully with {name}!{Colors.ENDC}")
                return result['url']
            else:
                error_msg = result['error'] if result['error'] else 'Timeout or unknown error'
                print(f"{Colors.RED}[✗] {name} failed: {error_msg[:40]}...{Colors.ENDC}")
                time.sleep(0.3)
                
        except Exception as e:
            print(f"\r{' ' * 70}\r", end='', flush=True)
            print(f"{Colors.RED}[✗] Error with {name}: {str(e)[:50]}...{Colors.ENDC}")
            continue
    
    # If all services failed
    print(f"{Colors.RED}[✗] All URL shortening services failed{Colors.ENDC}")
    return None


def create_masked_url(short_url, mask_text, custom_words=''):
    """
    Create masked URL using various techniques
    Format: https://mask-text@short-url or custom variations
    The browser will navigate to short-url but display mask-text in preview
    """
    # Extract the domain part from short URL (remove https://)
    short_domain = short_url.replace('https://', '').replace('http://', '')
    
    # Clean up mask_text
    mask_text = mask_text.replace('https://', '').replace('http://', '').strip()
    
    # If custom words provided, incorporate them
    if custom_words:
        custom_words = custom_words.strip().replace(' ', '-')
    
    # Create the masked URLs with different techniques
    
    # Method 1: Using @ symbol (Most Effective)
    if custom_words:
        masked_url_1 = f"https://{mask_text}-{custom_words}@{short_domain}"
    else:
        masked_url_1 = f"https://{mask_text}@{short_domain}"
    
    # Method 2: Using subdomain technique
    if custom_words:
        masked_url_2 = f"https://{custom_words}.{mask_text}.{short_domain}"
    else:
        masked_url_2 = f"https://{mask_text}.{short_domain}"
    
    # Method 3: Using URL path technique
    if custom_words:
        masked_url_3 = f"{short_url}/{custom_words}#{mask_text}"
    else:
        masked_url_3 = f"{short_url}#{mask_text}"
    
    # Method 4: Advanced - Question mark parameter trick
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


def main():
    """Main function to run the URL masker"""
    import time
    
    print_banner()
    
    # Show ethical disclaimer
    show_ethical_disclaimer()
    
    try:
        # Get original URL
        print(f"\n{Colors.BOLD}[1] Enter the Original URL{Colors.ENDC}")
        print(f"{Colors.CYAN}    (The actual target URL to redirect to){Colors.ENDC}")
        original_url = input(f"{Colors.GREEN}➜ {Colors.ENDC}").strip()
        
        if not original_url:
            print(f"{Colors.RED}[✗] No URL provided!{Colors.ENDC}")
            sys.exit(1)
        
        # Normalize and validate URL
        original_url = normalize_url(original_url)
        
        if not validate_url(original_url):
            print(f"{Colors.RED}[✗] Invalid URL format!{Colors.ENDC}")
            sys.exit(1)
        
        print(f"{Colors.GREEN}[✓] Valid URL: {original_url}{Colors.ENDC}")
        
        # Get custom mask domain
        print(f"\n{Colors.BOLD}[2] Enter the Masking Domain{Colors.ENDC}")
        print(f"{Colors.CYAN}    (The fake domain to display - e.g., google.com, facebook.com){Colors.ENDC}")
        mask_domain = input(f"{Colors.GREEN}➜ {Colors.ENDC}").strip()
        
        if not mask_domain:
            print(f"{Colors.RED}[✗] No mask domain provided!{Colors.ENDC}")
            sys.exit(1)
        
        # Get custom words/keywords
        print(f"\n{Colors.BOLD}[3] Enter Custom Keywords (Optional){Colors.ENDC}")
        print(f"{Colors.CYAN}    (Additional words to make URL look more legit - e.g., login, verify, account){Colors.ENDC}")
        print(f"{Colors.CYAN}    (Press Enter to skip){Colors.ENDC}")
        custom_words = input(f"{Colors.GREEN}➜ {Colors.ENDC}").strip()
        
        # Shorten the original URL using TinyURL
        short_url = shorten_url(original_url)
        
        if not short_url:
            print(f"\n{Colors.YELLOW}[!] URL shortening failed. Would you like to:{Colors.ENDC}")
            print(f"{Colors.CYAN}    [1] Use the original URL instead (may be longer){Colors.ENDC}")
            print(f"{Colors.CYAN}    [2] Exit and try again later{Colors.ENDC}")
            choice = input(f"{Colors.GREEN}➜ Enter choice (1 or 2): {Colors.ENDC}").strip()
            
            if choice == '1':
                short_url = original_url
                print(f"{Colors.GREEN}[✓] Using original URL{Colors.ENDC}")
            else:
                print(f"{Colors.RED}[✗] Exiting...{Colors.ENDC}")
                sys.exit(1)
        
        # Create masked URLs
        print(f"\n{Colors.YELLOW}[*] Creating masked URLs...{Colors.ENDC}")
        
        # Show progress bar
        import time
        for i in range(101):
            bar_length = 40
            filled = int(bar_length * i / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r{Colors.CYAN}[{bar}] {i}%{Colors.ENDC}", end='', flush=True)
            time.sleep(0.02)
        print()
        
        masked_urls = create_masked_url(short_url, mask_domain, custom_words)
        
        time.sleep(0.3)
        print(f"{Colors.GREEN}[✓] Masked URL generated!{Colors.ENDC}\n")
        time.sleep(0.3)
        
        # Display results with animation
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'':^70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'MASKED URL GENERATED':^70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'':^70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.ENDC}\n")
        
        time.sleep(0.2)
        
        print(f"{Colors.BOLD}Original URL:{Colors.ENDC}")
        print(f"  {Colors.CYAN}{original_url}{Colors.ENDC}\n")
        
        time.sleep(0.2)
        
        print(f"{Colors.BOLD}Shortened URL:{Colors.ENDC}")
        print(f"  {Colors.YELLOW}{masked_urls['original_short']}{Colors.ENDC}\n")
        
        time.sleep(0.2)
        
        print(f"{Colors.BOLD}{Colors.UNDERLINE}MASKED URL (Copy & Use):{Colors.ENDC}\n")
        
        time.sleep(0.3)
        
        # Typing effect for the masked URL
        print(f"{Colors.GREEN}{Colors.BOLD}", end='')
        for char in masked_urls['method_1']:
            print(char, end='', flush=True)
            time.sleep(0.02)
        print(f"{Colors.ENDC}\n")
        
        time.sleep(0.3)
        
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.ENDC}\n")
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}[✗] Operation cancelled by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}[✗] Error: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
