from socketserver import ThreadingTCPServer


class HealthCheckServer(ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True
    allow_reuse_port = True
