import http.server
import socketserver
import os
import argparse
from urllib.parse import unquote
import difflib
import hashlib
import re,subprocess
from urllib.request import urlretrieve
import difflib
import hashlib
import re, shutil
import tempfile
class FuzzyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        requested = unquote(self.path.lstrip("/"))
        full_base = os.getcwd()
        path_parts = requested.split("/")
        base_path = full_base
        remaining_parts = path_parts.copy()

        # Step 1: Resolve intermediate fuzzy directories (case-insensitive)
        for i, part in enumerate(path_parts[:-1]):
            dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
            mapping = {d.lower(): d for d in dirs}
            match = difflib.get_close_matches(part.lower(), mapping.keys(), n=1, cutoff=0.5)
            if match:
                real = mapping[match[0]]
                base_path = os.path.join(base_path, real)
                remaining_parts[i] = real
            else:
                break  # can't go deeper

        # Step 2: Handle final part (file or dir)
        final_part = path_parts[-1]
        try:
            entries = os.listdir(base_path)
        except Exception:
            entries = []

        mapping = {e.lower(): e for e in entries}
        full_target = os.path.join(base_path, mapping.get(final_part.lower(), final_part))

        if os.path.exists(full_target):
            remaining_parts[-1] = mapping.get(final_part.lower(), final_part)
            self.path = "/" + "/".join(remaining_parts)
            print(f"\033[94m[+] Exactly matched the file name '{requested.split('/')[-1]}' -> '{self.path}'	\033[0m")
            return super().do_GET()

        # Step 3: Try fuzzy match on final part
        matched = []
        candidates = list(mapping.keys())
        prefix_matches = [k for k in candidates if k.startswith(final_part.lower())]
        if prefix_matches:
            matched = [mapping[prefix_matches[0]]]
        else:
            fuzzy = difflib.get_close_matches(final_part.lower(), candidates, n=1, cutoff=0.5)
            if fuzzy:
                matched = [mapping[fuzzy[0]]]

        if matched:
            remaining_parts[-1] = matched[0]
            self.path = "/" + "/".join(remaining_parts)
            print(f"\033[92m[+] Fuzzy matched '{requested}' -> '{self.path}'\033[0m")
            return super().do_GET()

        # Step 4: No match — 404 response and list dirs on server side
        self.send_response(404)
        self.send_header("Content-type", "text/plain")
        self.send_header("Server-Reply", "No file matched.")
        self.end_headers()
        print(f"\033[91m[!] No exact or fuzzy match for '{requested}'.\033[0m")

        rel_path = "/" + "/".join(remaining_parts[:-1])
        abs_dir = os.path.join(self.directory, *remaining_parts[:-1])
        
        print(f"\033[95m[>] Available entries in {rel_path or '/'}:\033[0m\n")

        for f in sorted(entries):
            full_rel = os.path.join(rel_path, f).replace("\\", "/")
            abs_path = os.path.join(abs_dir, f)
            if os.path.isdir(abs_path):
                print(f"\033[94m{full_rel} (D)\033[0m")
            else:
                print(full_rel)

        print("\n") # for giving some gap in output

    def do_POST(self):
        requested = unquote(self.path.lstrip("/"))
        path_parts = requested.split("/")
        filename = path_parts[-1] or "default"

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"[!] Failed to read POST data.\n")
            print(f"[!] Error reading POST data: {e}")
            return

        # Compute MD5
        md5 = hashlib.md5(post_data).hexdigest()
        size_bytes = len(post_data)
        size_kb = size_bytes / 1024

        # Make sure the directory path exists
        dir_path = os.path.join(os.getcwd(), *path_parts[:-1])
        os.makedirs(dir_path, exist_ok=True)

        # Create the filename
        save_path = os.path.join(dir_path, f"fuzzy_post_data_{filename}")

        try:
            with open(save_path, "wb") as f:
                f.write(post_data)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"[!] Failed to write POST data to file.\n")
            print(f"[!] Error writing to file '{save_path}': {e}")
            return

        self.send_response(200)
        self.end_headers()
        message = (
            f"\n\n"
            f"\033[30;107m[+] POST data saved to: {save_path}\033[0m\n"
            f"\033[30;107m[+] Size: {size_bytes} bytes ({size_kb:.2f} KB)\033[0m\n"
            f"\033[30;107m[+] MD5: {md5}\033[0m\n"
            f"\n\n"
        )
        self.wfile.write(message.encode())
        print(message.strip())

# Methods to get all network interfaces and their IPs to keep this module self-contained
def get_network_interfaces():
    """Get all network interfaces and their IP addresses using ifconfig"""
    interfaces = []
    
    try:
        result = subprocess.run(['ifconfig'], 
                              capture_output=True, text=True, check=True)
        interfaces = parse_ifconfig_output(result.stdout)
        
    except subprocess.CalledProcessError:
        print("Error: ifconfig command failed")
        return []
    except FileNotFoundError:
        print("Error: ifconfig command not found")
        return []
    except Exception as e:
        print(f"Error getting network interfaces: {e}")
        return []
    
    return interfaces

def parse_ifconfig_output(output):
    """Parse output from ifconfig command"""
    interfaces = []
    current_interface = None
    
    for line in output.split('\n'):
        if line and not line.startswith(' ') and not line.startswith('\t'):
            interface_match = re.match(r'^([^:\s]+)', line)
            if interface_match:
                current_interface = interface_match.group(1)
        
        elif current_interface and ('inet ' in line or 'inet addr:' in line):
            
            ip_match = re.search(r'inet\s+(?:addr:)?([0-9.]+)', line)
            if ip_match:
                ip_address = ip_match.group(1)
                interfaces.append((current_interface, ip_address))
    
    return interfaces

def list_all_interfaces():
    print("Network Interfaces and IP Addresses:")
    print("-" * 40)
    
    interfaces = get_network_interfaces()
    
    if not interfaces:
        print("No network interfaces found with IP addresses.")
        return
    
    # Display results in the requested format
    for interface_name, ip_address in interfaces:
        if 'tun' in interface_name or 'eth' in interface_name:
            print(f"\033[35m{interface_name}: {ip_address}\033[0m")

    print("-" * 40)

def download_archive(github_url, dest_dir):
    """
    Download archive.7z from GitHub URL into dest_dir and return local path.
    """
    os.makedirs(dest_dir, exist_ok=True)
    local_path = os.path.join(dest_dir, os.path.basename(github_url))

    print(f"\033[94m[+] Downloading archive from: {github_url}\033[0m")
    urlretrieve(github_url, local_path)
    print(f"\033[92m[+] Saved archive to: {local_path}\033[0m")

    return local_path


def install_binaries(output_dir, github_url, seven_zip_path="7z"):
    """
    Download archive.7z from GitHub, extract into output_dir using given 7z binary.
    """
    os.makedirs(output_dir, exist_ok=True)
    archive_path = download_archive(github_url, tempfile.mkdtemp(prefix="fuzzy_dl_"))

    print(f"\033[94m[+] Installing binaries into: {output_dir}\033[0m")

    try:
        cmd = [
            seven_zip_path, "x", archive_path,
            "-p3ncrypt3d_m4lp4yl0ads",
            f"-o{output_dir}", "-y"
        ]
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"\033[91m[!] Extraction failed: {e}\033[0m")
        return

    # List installed folders
    print(f"\033[92m[+] Extraction completed. Installed folders:\033[0m")
    for entry in sorted(os.listdir(os.path.join(output_dir,"transfers"))):
        full_path = os.path.join(os.path.join(output_dir,"transfers"), entry)
        if os.path.isdir(full_path):
            print(f"   \033[96m{entry}/\033[0m")



# ---------------- Argument Parsing ---------------- #
parser = argparse.ArgumentParser(description="Fuzzy HTTP File Server", add_help=True)
parser.add_argument("-p", "--port", type=int, default=8000,
                    help="Port to serve on (default: 8000)")
parser.add_argument("-d", "--directory", type=str, default=os.getcwd(),
                    help="Directory to serve (default: current directory)")
parser.add_argument("-i", "--install", type=str,
                    help="Directory to install binaries into")
args = parser.parse_args()

# Handle install-only mode
if args.install:
    install_binaries(output_dir=args.install,github_url='https://github.com/PakCyberbot/fuzzy-httpserver/releases/download/1.5.0/transfers.7z')
    print("\033[93mFound a bug or have a feature request or more binaries suggestion? Reach out to @PakCyberbot (https://pakcyberbot.com) or create a pull request\033[0m")
    print("\033[1;38;5;51m[+] Feature coming soon:\033[0m "
    "Direct selection/download of specific binaries from URLs in fuzzy-httpserver.")
    exit(0)

# Start HTTP server
os.chdir(args.directory)
with socketserver.TCPServer(("", args.port), FuzzyHTTPRequestHandler) as httpd:
    print("\033[93mFound a bug or have a feature request? Reach out to @PakCyberbot (https://pakcyberbot.com)\033[0m")
    print(f"[+] Serving '{args.directory}' on port {args.port}")
    print()
    list_all_interfaces()
    print()
    httpd.serve_forever()
