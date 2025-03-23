# -------------------------------------------------------------------
# Programmer       : Ebrahim Shafiei (EbraSha)
# Email            : Prof.Shafiei@Gmail.com
# -------------------------------------------------------------------

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import undetected_chromedriver as uc
import time
import re
import sys
import ssl
import socket
import httpx
import random
from datetime import datetime
from colorama import init, Fore, Back, Style
init(autoreset=True)

uc.Chrome.__del__ = lambda self: None

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"
]


def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/"
    }


CDN_SIGNATURES = {
    "Cloudflare": ["cf-ray", "cf-cache-status", "server: cloudflare"],
    "Akamai": ["akamai", "x-akamai"],
    "Fastly": ["x-fastly", "fastly-debug"],
    "Amazon CloudFront": ["x-amz-cf-id", "via: cloudfront"],
    "Google Cloud CDN": ["x-goog-cdn", "server: gws"],
    "Microsoft Azure CDN": ["x-azure-ref"],
    "StackPath": ["stackpath"],
    "Sucuri": ["x-sucuri-id"],
    "ArvanCloud": ["ar-cache", "ar-powered", "server: arvancloud"]
}


def detect_cdn(headers):
    found_cdns = []
    headers_lower = {k.lower(): v.lower() for k, v in headers.items()}
    for cdn, patterns in CDN_SIGNATURES.items():
        for pattern in patterns:
            if ": " in pattern:
                key, value = pattern.lower().split(": ")
                if key in headers_lower and value in headers_lower[key]:
                    found_cdns.append(cdn)
            else:
                for header_key, header_value in headers_lower.items():
                    if pattern.lower() in header_key or pattern.lower() in header_value:
                        found_cdns.append(cdn)
    return list(set(found_cdns))


def check_http_features(url):
    try:
        with httpx.Client(http2=True, headers=get_headers(), timeout=10, follow_redirects=True) as client:
            response = client.get(url)
            return {
                "HTTP/2": response.http_version == "HTTP/2",
                "GZIP Compression": "gzip" in response.headers.get("content-encoding", "").lower(),
                "Brotli Compression": "br" in response.headers.get("content-encoding", "").lower(),
                "CDN": detect_cdn(response.headers)
            }
    except Exception:
        return {}


def check_quic(domain):
    try:
        context = ssl.create_default_context()
        context.set_alpn_protocols(["h3", "h3-29", "h3-28", "h3-27"])
        conn = socket.create_connection((domain, 443), timeout=5)
        sock = context.wrap_socket(conn, server_hostname=domain)
        alpn = sock.selected_alpn_protocol()
        sock.close()
        return {
            "HTTP/3": alpn.startswith("h3") if alpn else False,
            "QUIC": alpn.startswith("h3") if alpn else False
        }
    except:
        return {"HTTP/3": False, "QUIC": False}


def print_banner():
    # Get current date and time in a fancy format
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d | %H:%M:%S")

    # Colored datetime string (optional for terminal)
    fancy_time = f"{Fore.LIGHTGREEN_EX}{formatted_time}{Fore.LIGHTCYAN_EX}"

    banner = f"""
╔══════════════════════════════════════════════════════════════════╗
║  /$$$$$$  /$$$$$$$  /$$$$$$$   /$$$$$$  /$$                      ║
║ /$$__  $$| $$__  $$| $$__  $$ /$$__  $$| $$                      ║
║| $$  \\ $$| $$  \\ $$| $$  \\ $$| $$  \\ $$| $$                      ║
║| $$$$$$$$| $$$$$$$ | $$  | $$| $$$$$$$$| $$                      ║
║| $$__  $$| $$__  $$| $$  | $$| $$__  $$| $$                      ║
║| $$  | $$| $$  \\ $$| $$  | $$| $$  | $$| $$                      ║
║| $$  | $$| $$$$$$$/| $$$$$$$/| $$  | $$| $$$$$$$$                ║
║|__/  |__/|_______/ |_______/ |__/  |__/|________/                ║
║                                                                  ║
║                                                                  ║
║        Abdal Web Intelligence Analyzer v4.3                      ║
║                                                                  ║
║  [About] Abdal Web Intelligence Analyzer helps you analyze       ║
║          websites protected by services like Cloudflare,         ║
║          Akamai or ArvanCloud. It uses a real browser to         ║
║          bypass security layers, detect JS-based WAFs, extract   ║
║          static/dynamic requests, measure load time, and         ║
║          suggest safe request rates.                             ║
║                                                                  ║
   [Date Time] {fancy_time}                                         
╠══════════════════════════════════════════════════════════════════╣
║ DEVELOPER: Ebrahim Shafiei (EbraSha)                             ║
║ ENCRYPTED-COMMS: Prof.Shafiei@Gmail.com                          ║
║ SECURE-CHANNEL: @ProfShafiei                                     ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(Fore.LIGHTCYAN_EX + banner)


def is_arvan_protected(content, headers=None, cookies=None):
    keywords = [
        "Transferring to the website",
        "در ﺣﺎل اﻧﺘﻘﺎل ﺑﻪ ﺳﺎﯾﺖ",
        "static-pages-2.6.0.css",
        "__arcsjs="
    ]

    if any(k in content for k in keywords):
        return True

    if headers:
        server = headers.get("server", "").lower()
        if "arvancloud" in server:
            return True
        if any("x-sid" in h.lower() or "x-request-id" in h.lower() for h in headers.keys()):
            return True

    if cookies:
        for c in cookies:
            if c.get("name") == "__arcsjs":
                return True

    return False


def estimate_static_rate(cpu_cores, ram_gb, disk_type, os_type, total_requests):
    try:
        score = (cpu_cores * 10) + (ram_gb * 5)
        score *= {"hdd": 0.6, "ssd": 1.0, "nvme": 1.5}.get(disk_type.lower(), 1.0)
        if os_type.lower() == "linux":
            score *= 1.2
        return max(5, min(int(score), total_requests))
    except:
        return max(5, min(total_requests // 5, 50))


def detect_dynamic_requests(page_content, base_url):
    try:
        patterns = [
            r'fetch\(["\'](.*?)["\']',
            r'\.ajax\(\s*{[^}]*url\s*:\s*["\'](.*?)["\']',
            r'axios\.(get|post|put|delete)\(["\'](.*?)["\']',
            r'XMLHttpRequest',
            r'["\'](/(api|ajax|data|post|submit|update|search)[^"\']*)["\']',
            r'["\'](/[^"\']*\?(.*?)=.*?)["\']',
            r'["\']([^"\']+\.(php|asp|aspx|jsp|json|xml|cgi))["\']',
        ]
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, page_content, flags=re.IGNORECASE)
            if not found: continue
            if isinstance(found[0], tuple):
                flat = []
                for item in found:
                    for sub in item:
                        if sub and not sub.lower().startswith(('get', 'post', 'put', 'delete')):
                            flat.append(sub)
                found = flat
            matches.extend(found)
        soup = BeautifulSoup(page_content, "html.parser")
        forms = soup.find_all("form", action=True)
        for form in forms:
            matches.append(urljoin(base_url, form["action"]))
        return [urljoin(base_url, link) for link in set(matches) if
                isinstance(link, str) and not link.endswith(('.js', '.css', '.png', '.jpg', '.woff', '.svg'))]
    except:
        return []


def get_static_requests(url, cpu_cores=None, ram_gb=None, disk_type=None, os_type=None):
    parsed = urlparse(url)
    base = parsed.netloc or parsed.path
    proto_info = {**check_http_features(url), **check_quic(base)}

    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    browser = None
    try:
        browser = uc.Chrome(options=options)
        browser.get(url)
        time.sleep(3)

        page_content = browser.page_source
        cookies = browser.get_cookies()
        headers = {"server": browser.execute_script("return document.location.hostname")}

        if is_arvan_protected(page_content, headers=headers, cookies=cookies):
            print("🛡️ ArvanCloud WAF detected. Waiting for bypass...")
            time.sleep(6)
            page_content = browser.page_source

        try:
            timing = browser.execute_script("return window.performance.timing")
            load_time = round((timing["loadEventEnd"] - timing["navigationStart"]) / 1000, 2)
        except:
            load_time = None

        soup = BeautifulSoup(page_content, 'html.parser')
        static_files = {
            'images': [urljoin(url, img['src']) for img in soup.find_all('img', src=True)],
            'css': [urljoin(url, link['href']) for link in soup.find_all('link', rel='stylesheet', href=True)],
            'js': [urljoin(url, script['src']) for script in soup.find_all('script', src=True)],
            'fonts': [urljoin(url, link['href']) for link in soup.find_all('link', rel='stylesheet', href=True) if
                      'fonts' in link['href']]
        }

        dynamic_files = detect_dynamic_requests(page_content, url)
        total_static = sum(len(files) for files in static_files.values())
        total_dynamic = len(dynamic_files)

        print(f"\n🔍 Analyzing: {url}")
        print("=====================================")
        if load_time: print(f"⏱️ Page Load Time: {load_time} seconds")
        if is_arvan_protected(page_content, headers=headers, cookies=cookies):
            print(f"🌐 CDN Detected: ArvanCloud ")
        else:
            for key, val in proto_info.items():
                if key == "CDN":
                    print(f"🌐 CDN Detected: {', '.join(val) if val else 'None'}")
                else:
                    print(f"{key} Supported: {'✅' if val else '❌'}")

        print(f"📸 Images: {len(static_files['images'])}")
        print(f"🎨 CSS Files: {len(static_files['css'])}")
        print(f"📜 JS Files: {len(static_files['js'])}")
        print(f"🔠 Fonts: {len(static_files['fonts'])}")
        print(f"⚙️ Dynamic Requests: {total_dynamic}")
        print("-------------------------------------")
        print(f"📊 Total Static Requests: {total_static}")
        print(f"📊 Total Dynamic Requests: {total_dynamic}")

        if all([cpu_cores, ram_gb, disk_type, os_type]):
            static_rps = estimate_static_rate(cpu_cores, ram_gb, disk_type, os_type, total_static)
            dynamic_rps = estimate_static_rate(cpu_cores, ram_gb, disk_type, os_type, total_dynamic // 2)
        else:
            static_rps = max(5, min(total_static // 5, 50))
            dynamic_rps = max(3, min(total_dynamic // 4, 40))

        print(f"\n⚙️ Suggested Static RPS: {static_rps}")
        print(f"⚙️ Suggested Dynamic RPS: {dynamic_rps}\n")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if browser:
            try:
                browser.quit()
            except:
                pass


if __name__ == "__main__":

    print_banner()

    url = input(Back.BLACK + Fore.LIGHTMAGENTA_EX + Style.BRIGHT  +"🔗 Enter website URL (with http/https): ").strip()

    try:
        cpu_input = input("🧠 CPU cores? (Enter to skip): ").strip()
        ram_input = input("💾 RAM in GB? (Enter to skip): ").strip()
        disk_input = input("💽 Disk type (HDD/SSD/NVMe)? (Enter to skip): ").strip()
        os_input = input("🖥️ OS (Linux/Windows)? (Enter to skip): ").strip()
        print(Style.RESET_ALL)
        cpu_cores = int(cpu_input) if cpu_input else None
        ram_gb = int(ram_input) if ram_input else None
        disk_type = disk_input if disk_input else None
        os_type = os_input if os_input else None
    except:
        cpu_cores = ram_gb = disk_type = os_type = None

    try:
        get_static_requests(url, cpu_cores, ram_gb, disk_type, os_type)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted.")
        sys.exit(0)
