import socket
import threading
from collections import deque

"""
main thread
    open socket
    recieve packet
    for endpoint in endpoints
        spawn worker thread(endpoint)
    

worker thread(endpoint
    open socket to endpoint
    send data to endpoint
    wait for data
    is there any data?
        reply
    
    close
"""


class LoadBalancer(object):
    def __init__(self, bind_address = '0.0.0.0',
                       bind_port = 27900,
                       endpoints = None):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.endpoints = EndpointLoader()

    def listen(self):
        while True:
            client, address = self.server_socket.accept()
            client.settimeout(60)
            
            endpoint = self.endpoints.fetch_endpoint

            threading.Thread(target = SocketWorker(),
                             args = (client, address, endpoint))

    def __del__(self):
        self.server_socket.close()


class SocketWorker(object):
    def __init__(self, client, address, endpoint):
        """
        TODO: create new socket
        TODO: send data to endpoint
        """
        self.client_connection = client
        self.client_address = address
        self.endpoint = endpoint
        self.work()

    def work(self):
        while True:
            try:
                data = self.client_socket.recv(4096)
                if data:
                    self.endpoint_connection(data)
                else:
                    pass
            except:
                return False

    def endpoint_connection(self, data):
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as endpoint_socket:
            endpoint_socket.sendall(data)
        pass

    def __del__(self):
        self.client_connection.close()


class EndpointLoader(object):
    def __init__(self):
        self.endpoints = self.load_endpoints()

    def load_endpoints(self):
        endpoints = deque()
        module_path = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.join(module_path, 'config', 'endpoints.yml')
        with open(config_path, 'rb') as config_file_handle:
            config = yaml.load(config_file_handle, Loader=yaml.FullLoader)
            for endpoint in config:
                endpoints.append(Endpoint(endpoint))

        return endpoints

    @property
    def fetch_endpoint(self):
        self.endpoints.rotate(-1)
        return self.endpoints[0]



class Endpoint(object):
    def __init__(self, config):
        self.host = config.get('host')
        self.port = config.get('port')
        self.uri = ':'.join([self.host, self.port])
        self.active = config.get('active')

    @property
    def host(self):
        return self.host

    @property
    def port(self):
        return self.port

    @property
    def uri(self):
        return self.uri

    @property
    def active(self):
        return self.active


def main():
    endpoints = Endpoints()

    LoadBalancer(bind_address = '0.0.0.0',
                 bind_port = 27900,
                 endpoints = endpoints).listen()


if __name__ == '__main__':
    main()

