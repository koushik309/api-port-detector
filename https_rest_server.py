from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import json

html_page = b"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>REST API UI</title>
    <style>
        body { font-family: Arial; padding: 2em; background: #f0f0f0; }
        h1 { color: #333; }
        #result { margin-top: 1em; padding: 1em; background: #fff; border: 1px solid #ccc; }
    </style>
</head>
<body>
    <h1>REST API UI</h1>
    <button onclick="callApi()">Call API</button>
    <div id="result">Waiting for response...</div>
    <script>
        async function callApi() {
            try {
                const res = await fetch('/api');
                const json = await res.json();
                document.getElementById('result').textContent = JSON.stringify(json, null, 2);
            } catch (err) {
                document.getElementById('result').textContent = "Error: " + err;
            }
        }
    </script>
</body>
</html>
"""

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/ui":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html_page)
        elif self.path in ["/", "/api", "/swagger", "/openapi", "/health"]:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("API-Version", "1.0")
            self.end_headers()
            self.wfile.write(json.dumps({"message": "REST API is active"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run():
    server_address = ('127.0.0.1', 60000)
    httpd = HTTPServer(server_address, SimpleHandler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    print("✅ HTTPS REST API server running at https://127.0.0.1:60000")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
