import socket
import subprocess
import re
import psutil
from http.client import HTTPConnection
import time

def get_processes_by_port(port):
    """Find processes listening on a specific port"""
    try:
        # Use netstat to find processes by port
        netstat = subprocess.run(
            ['netstat', '-ano', '-p', 'tcp'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse netstat output
        processes = []
        for line in netstat.stdout.splitlines():
            if 'LISTENING' in line and f":{port}" in line:
                parts = re.split(r'\s+', line.strip())
                pid = parts[-1]
                try:
                    proc = psutil.Process(int(pid))
                    processes.append({
                        'pid': pid,
                        'name': proc.name(),
                        'exe': proc.exe(),
                        'cmdline': ' '.join(proc.cmdline()),
                        'status': proc.status()
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
                    processes.append({
                        'pid': pid,
                        'name': 'Unknown',
                        'exe': 'Unknown',
                        'cmdline': 'Unknown',
                        'status': 'Unknown'
                    })
        return processes
    except Exception as e:
        print(f"Error getting processes for port {port}: {str(e)}")
        return []

def is_port_open(port):
    """Check if a port is open using socket"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

def detect_rest_api(port, timeout=2.0):
    """Detect if a port is serving a REST API"""
    try:
        # Try HTTP connection
        conn = HTTPConnection('localhost', port, timeout=timeout)
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
        for endpoint in ['/api', '/swagger', '/openapi', '/health']:
            try:
                conn.request("GET", endpoint)
                response = conn.getresponse()
                if response.status < 400:  # 2xx or 3xx response
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

def main():
    ports_to_check = [60000, 80, 443, 8080, 8000, 5000, 3000, 8443, 8081]
    
    print("[*] Starting REST API server detection")
    print(f"[*] Checking ports: {ports_to_check}")
    
    for port in ports_to_check:
        print(f"\n[+] Checking port {port}")
        
        # Check if port is open
        if is_port_open(port):
            print(f"    [*] Port {port} is open")
            
            # Find processes using this port
            processes = get_processes_by_port(port)
            if processes:
                print(f"    [*] Found {len(processes)} process(es) using this port:")
                for i, proc in enumerate(processes, 1):
                    print(f"        {i}. PID: {proc['pid']}")
                    print(f"           Name: {proc['name']}")
                    print(f"           Path: {proc['exe']}")
                    print(f"           Cmd: {proc['cmdline'][:100]}{'...' if len(proc['cmdline']) > 100 else ''}")
                    print(f"           Status: {proc['status']}")
            else:
                print("    [*] No processes found for this port (might be a system service)")
            
            # Check if it's a REST API
            if detect_rest_api(port):
                print(f"    [*] REST API detected on port {port}")
            else:
                print(f"    [*] No REST API detected on port {port}")
        else:
            print(f"    [*] Port {port} is closed")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[!] Critical error: {str(e)}")