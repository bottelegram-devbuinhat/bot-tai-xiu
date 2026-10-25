from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class h(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run():
    s = HTTPServer(('0.0.0.0', 8080), h)
    s.serve_forever()

def k():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()