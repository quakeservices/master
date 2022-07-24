import logging
from socketserver import StreamRequestHandler


class HealthCheckHandler(StreamRequestHandler):
    def handler(self) -> None:
        logging.debug("Received health check ping")
        response: bytes = (
            b"HTTP/1.1 200 OK\nContent-Type: text/html\n<html><body>OK</body></html>\n"
        )
        self.wfile.write(response)
