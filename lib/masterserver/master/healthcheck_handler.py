from socketserver import StreamRequestHandler

from helpers import LoggingMixin


class HealthCheckHandler(StreamRequestHandler, LoggingMixin):
    def handler(self):
        self.log("Received health check ping")
        self.log(self.request.recv(1024))
        response: bytes = (
            b"HTTP/1.1 200 OK\nContent-Type: text/html\n<html><body>OK</body></html>\n"
        )
        self.wfile.write(response)
