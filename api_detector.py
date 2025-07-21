import socket
import sys
import time
import os
import re
import subprocess
import psutil
from http.client import HTTPConnection, HTTPSConnection
import ssl
import argparse

def get_processes_by_port(port):
    """Find processes listening on a specific port using psutil (cross-platform)"""
    processes = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'LISTEN' and conn.laddr.port == port:
            try:
                proc = psutil.Process(conn.pid)
                processes.append({
                    'pid': conn.pid,
                    'name': proc.name(),
                    'exe': proc.exe(),
                    'cmdline': ' '.join(proc.cmdline()),
                    'status': proc.status()
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                processes.append({
                    'pid': conn.pid,
                    'name': 'Unknown',
                    'exe': 'Unknown',
                    'cmdline': 'Unknown',
                    'status': 'Unknown'
                })
    return processes

def is_port_open(port):
    """Check if a port is open using socket"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

def detect_rest_api(port, timeout=2.0):
    """Detect if a port is serving a REST API with HTTPS support"""
    # Try HTTPS first for secure APIs
    try:
        context = ssl._create_unverified_context()
        conn = HTTPSConnection('localhost', port, timeout=timeout, context=context)
        conn.request("GET", "/")
        response = conn.getresponse()
        
        # Check for common REST API indicators
        headers = response.getheaders()
        content_type = dict(headers).get('Content-Type', '').lower()
        response_body = response.read().decode('utf-8', 'ignore').lower()
        
        # REST API indicators
        if 'application/json' in content_type:
            return True
        if 'api' in response_body or 'rest' in response_body:
            return True
        if any(header[0].lower() == 'api-version' for header in headers):
            return True
            
        # Try common API endpoints
        for endpoint in ['/api', '/swagger', '/openapi', '/health', '/status']:
            try:
                conn.request("GET", endpoint)
                response = conn.getresponse()
                if response.status < 400:  # 2xx or 3xx response
                    return True
            except:
                continue
                
        return False
    except Exception:
        # Try HTTP connection if HTTPS fails
        try:
            conn = HTTPConnection('localhost', port, timeout=timeout)
            conn.request("GET", "/")
            response = conn.getresponse()
            
            headers = response.getheaders()
            content_type = dict(headers).get('Content-Type', '').lower()
            response_body = response.read().decode('utf-8', 'ignore').lower()
            
            if 'application/json' in content_type:
                return True
            if 'api' in response_body or 'rest' in response_body:
                return True
            if any(header[0].lower() == 'api-version' for header in headers):
                return True
                
            for endpoint in ['/api', '/swagger', '/openapi', '/health', '/status']:
                try:
                    conn.request("GET", endpoint)
                    response = conn.getresponse()
                    if response.status < 400:
                        return True
                except:
                    continue
                    
            return False
        except Exception:
            # Try generic socket connection if HTTP fails
            try:
                with socket.create_connection(('localhost', port), timeout=timeout) as s:
                    s.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
                    time.sleep(0.2)
                    response = s.recv(1024).decode('utf-8', 'ignore').lower()
                    if 'http' in response or 'api' in response:
                        return True
            except:
                return False
    return False

def print_banner():
    """Print a colorful banner for the tool"""
    banner = r"""
     ____  _____ ____ _____   ____ ___ _   _ ____  ____  
    |  _ \| ____/ ___|_   _| |  _ \_ _| \ | |  _ \/ ___| 
    | |_) |  _| \___ \ | |   | | | | ||  \| | | | \___ \ 
    |  _ <| |___ ___) || |   | |_| | || |\  | |_| |___) |
    |_| \_\_____|____/ |_|   |____/___|_| \_|____/|____/ 
    """
    print("\033[1;34m" + banner + "\033[0m")
    print("\033[1;36mREST API Server Detection Tool - v1.0\033[0m")
    print("\033[1;36mCross-Platform Solution for Windows, Linux, and Containers\033[0m\n")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Detect REST API servers running on the system')
    parser.add_argument('--ports', type=str, default='60000,80,443,8080,8000,5000,3000,8443,8081',
                        help='Comma-separated list of ports to check')
    parser.add_argument('--timeout', type=float, default=2.0,
                        help='Timeout for API detection in seconds')
    parser.add_argument('--output', type=str, default='',
                        help='Output file to save results')
    args = parser.parse_args()

    # Convert ports to integers
    try:
        ports_to_check = [int(port) for port in args.ports.split(',')]
    except ValueError:
        print("Invalid port list. Please provide comma-separated integers.")
        sys.exit(1)

    # Print banner
    print_banner()
    
    # Prepare output
    output_lines = []
    output_lines.append(f"[*] Starting REST API server detection")
    output_lines.append(f"[*] Checking ports: {ports_to_check}")
    output_lines.append(f"[*] Timeout: {args.timeout} seconds\n")
    
    detected_servers = []
    
    for port in ports_to_check:
        port_output = []
        port_output.append(f"[+] Checking port {port}")
        
        # Check if port is open
        if is_port_open(port):
            port_output.append(f"    [*] Port {port} is open")
            
            # Find processes using this port
            processes = get_processes_by_port(port)
            if processes:
                port_output.append(f"    [*] Found {len(processes)} process(es) using this port:")
                for i, proc in enumerate(processes, 1):
                    port_output.append(f"        {i}. PID: {proc['pid']}")
                    port_output.append(f"           Name: {proc['name']}")
                    port_output.append(f"           Path: {proc['exe']}")
                    port_output.append(f"           Cmd: {proc['cmdline'][:100]}{'...' if len(proc['cmdline']) > 100 else ''}")
                    port_output.append(f"           Status: {proc['status']}")
            else:
                port_output.append("    [*] No processes found for this port (might be a system service)")
            
            # Check if it's a REST API
            if detect_rest_api(port, args.timeout):
                port_output.append(f"    [*] \033[1;32mREST API detected on port {port}\033[0m")
                detected_servers.append(port)
            else:
                port_output.append(f"    [*] \033[1;31mNo REST API detected on port {port}\033[0m")
        else:
            port_output.append(f"    [*] Port {port} is closed")
        
        # Add port output to main output
        output_lines.extend(port_output)
        output_lines.append("")  # Add empty line for separation
    
    # Print summary
    if detected_servers:
        output_lines.append("\n[+] Summary of detected REST API servers:")
        for port in detected_servers:
            output_lines.append(f"    - Port {port} is running a REST API service")
    else:
        output_lines.append("\n[-] No REST API servers found")
    
    # Print to console with colors
    for line in output_lines:
        if "REST API detected" in line:
            print(line)
        elif "No REST API detected" in line:
            print(line)
        else:
            print(line.replace('[*]', '\033[1;33m[*]\033[0m')
                  .replace('[+]', '\033[1;32m[+]\033[0m')
                  .replace('[-]', '\033[1;31m[-]\033[0m'))
    
    # Save to file if requested
    if args.output:
        try:
            with open(args.output, 'w') as f:
                # Remove color codes for file output
                clean_output = [re.sub(r'\033\[[0-9;]*m', '', line) for line in output_lines]
                f.write("\n".join(clean_output))
            print(f"\n[+] Results saved to {args.output}")
        except Exception as e:
            print(f"[-] Failed to save results: {str(e)}")

if __name__ == "__main__":
    try:
        # Check if psutil is installed
        import psutil
        main()
    except ImportError:
        print("psutil module is required. Please install it with: pip install psutil")
        sys.exit(1)