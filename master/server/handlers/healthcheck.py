from socketserver import StreamRequestHandler

PROTOCOL: str = "HTTP/1.1"
STATUS: str = "200"
STATUS_TEXT: str = "OK"
NEWLINE: str = "\r\n"
RESPONSE_TEXT: str = "Success!"
RESPONSE: bytes = (
    f"{PROTOCOL} {STATUS} {STATUS_TEXT}{NEWLINE}{NEWLINE}{RESPONSE_TEXT}".encode(
        "utf-8"
    )
)


class HealthCheckHandler(StreamRequestHandler):
    def handle(self) -> None:
        # logging.debug("Received health check ping")
        self.wfile.write(RESPONSE)
