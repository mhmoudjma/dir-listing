#Dir-Listing
A fast, lightweight, and multi-threaded Python tool designed to detect exposed **Directory Listing** (Autoindex) endpoints from discovery outputs (such as `dirsearch`)

# 🚀 Features

- **Multi-threaded Scanning:** High-performance URL verification using Python's `ThreadPoolExecutor`.
- **Advanced Signature Matching:** Uses regex to detect Apache, Nginx, IIS, and generic directory index signatures.
- **Flexible Pipeline Integration:** Accepts input from a file or directly via standard input (`stdin`).
- **URL Normalization & Deduplication:** Prevents duplicate outputs and handles relative/absolute URLs gracefully.

##  Installation
'''bash 
git clone https://github.com/mhmoudjma/dir-listing 
cd dir-listing
'''

## HOW TO USE IT 
'''bash
dirsearch -u https://EXMPILE.COM | python3 dir-listing.py 
'''
## HOW IT WORK?
1-Extraction: Parses full URLs and relative paths from standard input or files.

2-Analysis: Sends GET requests using multi-threading and checks the response content against known directory listing signatures.

3-Filtering: Deduplicates verified URLs and prints live color-coded findings directly to the console.

## Disclaimer

This tool is developed for security research, penetration testing, and ethical auditing purposes only. Unlawful use of this tool against target infrastructure without explicit permission is strictly prohibited.

## Author

Developed by Mhmoud jma
