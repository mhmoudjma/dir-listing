#!/usr/bin/env python3
import argparse
import re
import sys
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin

# الألوان لأسلوب Metasploit
R = "\033[31m"  # Red
G = "\033[32m"  # Green
Y = "\033[33m"  # Yellow
B = "\033[34m"  # Blue
C = "\033[36m"  # Cyan
RESET = "\033[0m"

BANNER = f"""{C}
  ____  _       _     _     _   _                   
 |  _ \(_)_ __ | |   (_)___| |_(_)_ __   __ _       
 | | | | | '__|| |   | / __| __| | '_ \ / _` |      
 | |_| | | |   | |___| \__ \ |_| | | | | (_| |      
 |____/|_|_|   |_____|_|___/\__|_|_| |_|\__, |      
                                        |___/       
{RESET}{Y}           [ Directory Listing Scanner v1.0 ]
       [ Developer: Mhmoud Jma  ]{RESET}
"""

SIGNATURES = [
    r"<title>\s*Index of /",
    r"<title>\s*Directory listing for",
    r"Parent Directory",
    r"Directory Listing For",
    r"Index of /",
    r"Apache.*autoindex",
    r"nginx.*autoindex",
    r"Directory listing",
    r"\[To Parent Directory\]",
    r"C=N;O=D",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# قفل لمنع التضارب بين الخيوط (Threads) أثناء طباعة النتائج وحفظها
print_lock = threading.Lock()
seen_urls = set()

def extract_urls(text, base_url=None):
    cleaned = set()

    # 1. استخراج الروابط الكاملة (-F)
    full_urls = re.findall(r'https?://[^\s\]\[<>"\']+', text)
    for url in full_urls:
        url = url.rstrip("),.;:'\"")
        parsed = urlparse(url)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            cleaned.add(url)

    # 2. استخراج المسارات النسبية
    if base_url:
        paths = re.findall(r'(?<=\s)/[^\s\]\[<>"\']+', text)
        for path in paths:
            path = path.rstrip("),.;:'\"")
            full_url = urljoin(base_url, path)
            cleaned.add(full_url)

    return sorted(cleaned)


def is_directory_listing(url, timeout=8):
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True,
            verify=False
        )

        content = response.text[:500000]

        for signature in SIGNATURES:
            if re.search(signature, content, re.I | re.S):
                return True, response.url, response.status_code

        return False, response.url, response.status_code

    except requests.RequestException:
        return False, url, None


def main():
    # طباعة شعار الأداة في البداية زي ميتاسبلويت
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="Find Directory Listing URLs from Dirsearch output."
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Dirsearch output file. Use '-' for stdin."
    )

    parser.add_argument(
        "-u",
        "--url",
        help="Base Target URL (e.g., https://example.com) required if Dirsearch wasn't run with -F"
    )

    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=10,
        help="Number of concurrent requests (default: 10)"
    )

    args = parser.parse_args()

    if args.file == "-" or args.file is None:
        data = sys.stdin.read()
    else:
        with open(args.file, "r", errors="ignore") as f:
            data = f.read()

    urls = extract_urls(data, base_url=args.url)

    if not urls:
        print(f"{R}[-] No valid URLs found. Make sure Dirsearch output used -F or provide -u/--url argument.{RESET}")
        sys.exit(1)

    print(f"{G}[+]{RESET} Found {len(urls)} unique input URLs to check")
    print(f"{G}[+]{RESET} Checking for directory listings...\n")

    found_unique = set()

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {
            executor.submit(is_directory_listing, url): url
            for url in urls
        }

        for future in as_completed(futures):
            try:
                is_listing, final_url, status = future.result()

                if is_listing:
                    normalized_url = final_url.rstrip("/") + "/"

                    with print_lock:
                        if normalized_url not in seen_urls:
                            seen_urls.add(normalized_url)
                            found_unique.add(normalized_url)
                            print(f"{G}[+] DIRECTORY LISTING [{status}]{RESET} {normalized_url}")

            except Exception:
                pass

    print("\n" + "=" * 60)
    print(f"{C}Unique Directory Listings Found: {len(found_unique)}{RESET}")
    print("=" * 60)

    for url in sorted(found_unique):
        print(url)


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    main()
