import os
import threading
from queue import Queue
from socketserver import ThreadingMixIn, UDPServer


class ThreadPoolServer(ThreadingMixIn, UDPServer):
    allow_reuse_port: bool = True
    allow_reuse_address: bool = True
    cpu_count: int = os.cpu_count() or 1
    # TODO: Have a max_thread_pool_size
    thread_pool_size: int = cpu_count * 1
    requests: Queue = Queue(thread_pool_size)
    _shutdown: bool = False

    # pylint: disable=arguments-differ
    def serve_forever(self):

        for _ in range(self.thread_pool_size):
            thread = threading.Thread(target=self.process_request_thread)
            thread.daemon = True
            thread.start()

        while not self._shutdown:
            self.handle_request()

        self.terminate()
        self.server_close()

    # pylint: disable=arguments-differ
    def process_request_thread(self):
        while not self._shutdown:
            ThreadingMixIn.process_request_thread(self, *self.requests.get())

    def handle_request(self):
        try:
            request, client_address = self.get_request()
        except OSError:
            return

        self.requests.put((request, client_address))

    def terminate(self):
        self._shutdown = True
