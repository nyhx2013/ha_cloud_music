from http.server import HTTPServer, BaseHTTPRequestHandler

data = "[]"
host = ('localhost', 8321)

class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        path = str(self.path)
        if path == "/ble":
            self.wfile.write(data.encode())
        else:
            self.wfile.write("404".encode())

if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
