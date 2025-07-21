# REST API Server Detection Tool

![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

This Python tool detects REST API servers running on your system by:
1. Scanning specified ports to identify active services
2. Identifying processes associated with each open port
3. Analyzing responses to verify REST API characteristics
4. Providing detailed information about detected API servers

## Features

- 🔍 Port scanning with customizable port lists
- 🖥️ Process identification (PID, executable path, command line)
- 🌐 REST API verification through response analysis
- 📊 Detailed reporting of detected API servers
- 🚀 Executable builder for easy distribution

## Requirements

- Windows operating system
- Python 3.6 or higher
- Administrator privileges (for full functionality)
- Build tools (for creating .exe)

## Installation

1. Clone the repository or download the script:
```bash
git clone https://github.com/yourusername/rest-api-detector.git
cd rest-api-detector
```

2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install pyinstaller psutil
```

## Usage

### Basic Detection
```bash
python detect_rest_servers.py
```

### Custom Port Configuration
Edit the `ports_to_check` list in the script to include your specific ports:
```python
ports_to_check = [60000, 60001, 8080, 5000]  # Add your ports here
```

### Build Executable (.exe)
```bash
pyinstaller --onefile --name "APIServerDetector" --icon "api_icon.ico" --console detect_rest_servers.py
```

The executable will be created in the `dist` folder.

### Run Executable
```bash
dist\APIServerDetector.exe
```

### Command Line Options
```bash
# Scan specific ports
APIServerDetector.exe --ports 60000,8080,5000

# Increase timeout for slow-responding servers
APIServerDetector.exe --timeout 5

# Save results to a file
APIServerDetector.exe --output results.txt
```

## How to Set Up the .exe File

### 1. Build the Executable
Use PyInstaller to create a standalone executable:
```bash
pyinstaller --onefile --name "APIServerDetector" --console detect_rest_servers.py
```

### 2. Customize the Build (Optional)
- Add an icon:
  ```bash
  pyinstaller --onefile --name "APIServerDetector" --icon "api_icon.ico" --console detect_rest_servers.py
  ```
- Remove console window:
  ```bash
  pyinstaller --onefile --name "APIServerDetector" --noconsole detect_rest_servers.py
  ```
- Add version information:
  Create `version_info.txt`:
  ```
  # UTF-8
  VSVersionInfo(
    ffi=FixedFileInfo(
      filevers=(1, 0, 0, 0),
      prodvers=(1, 0, 0, 0),
      mask=0x3f,
      flags=0x0,
      OS=0x40004,
      fileType=0x1,
      subtype=0x0,
      date=(0, 0)
    ),
    kids=[
      StringFileInfo(
        [
          StringTable(
            '040904B0',
            [StringStruct('CompanyName', "Your Company"),
             StringStruct('FileDescription', "REST API Server Detector"),
             StringStruct('FileVersion', "1.0.0.0"),
             StringStruct('InternalName', "APIServerDetector"),
             StringStruct('LegalCopyright', "Copyright © 2023 Your Company"),
             StringStruct('OriginalFilename', "APIServerDetector.exe"),
             StringStruct('ProductName', "API Server Detector"),
             StringStruct('ProductVersion', "1.0.0.0")])
        ]), 
      VarFileInfo([VarStruct('Translation', [1033, 1200])])
    ]
  )
  ```
  Then build with:
  ```bash
  pyinstaller --onefile --name "APIServerDetector" --version-file version_info.txt detect_rest_servers.py
  ```

### 3. Distribute the Executable
- The standalone executable is in the `dist` folder
- No dependencies needed - runs on any Windows machine
- Ideal for systems without Python installed

## How It Works

1. **Port Scanning**:
   - Checks specified ports to identify open connections
   - Uses socket connections for reliable detection

2. **Process Identification**:
   - Uses `netstat` to find processes associated with each port
   - Uses `tasklist` to get detailed process information

3. **API Verification**:
   - Sends HTTP requests to potential API endpoints
   - Analyzes responses for REST characteristics:
     - JSON content types
     - API-related keywords in responses
     - Standard API endpoints (/api, /swagger, etc.)
   - Validates HTTP status codes

4. **Reporting**:
   - Displays detailed information about detected API servers
   - Shows process details and verification status

## Sample Output
```
[*] Starting REST API server detection
[*] Checking ports: [60000, 60001, 8080]

[+] Checking port 60000
    [*] Port 60000 is open
    [*] Found 1 process(es) using this port:
        1. PID: 1234
           Name: my_server.exe
           Path: C:\Program Files\MyServer\my_server.exe
           Cmd: my_server.exe --port 60000 --api
           Status: running
    [*] REST API detected on port 60000

[+] Checking port 60001
    [*] Port 60001 is closed

[+] Checking port 8080
    [*] Port 8080 is open
    [*] Found 1 process(es) using this port:
        1. PID: 5678
           Name: python.exe
           Path: C:\Python39\python.exe
           Cmd: python api_server.py
           Status: running
    [*] REST API detected on port 8080

[+] Summary of detected REST API servers:
    - Port 60000: my_server.exe (PID: 1234)
    - Port 8080: python.exe (PID: 5678)
```

## Troubleshooting

### Common Issues
1. **Port shows as closed but server is running**:
   - Ensure server is bound to 0.0.0.0 or 127.0.0.1
   - Check firewall settings
   - Verify the server is actually running

2. **Process information not available**:
   - Run script as Administrator
   - Some system processes might hide information

3. **API verification fails**:
   - Add custom endpoints to the `detect_rest_api` function
   - Increase timeout with `--timeout` option
   - Check if API requires authentication

### Manual Verification
Check what's running on a specific port:
```powershell
netstat -ano | findstr ":60000"
tasklist /FI "PID eq 1234"
```

Test API manually:
```powershell
curl http://localhost:60000/api/status
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any:
- Bug fixes
- Feature enhancements
- Documentation improvements
- Additional API detection methods
