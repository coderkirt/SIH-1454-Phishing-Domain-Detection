"""Serve PhishEye.apk on the LAN so a phone can download it."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)


class Handler(SimpleHTTPRequestHandler):
    def guess_type(self, path):
        if str(path).lower().endswith(".apk"):
            return "application/vnd.android.package-archive"
        return super().guess_type(path)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.path = "/download.html"
        return super().do_GET()


if __name__ == "__main__":
    host, port = "0.0.0.0", 8765
    print(f"PhishEye APK at http://{host}:{port}/PhishEye.apk")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
