#!/usr/bin/env python3
from storage import Storage
from transport import Transport
from headers import Headers

from masterserver import MasterServer


# Socket example:
my_socket_server = MasterServer(Storage('dynamodb'), Transport('socket'), Headers())
# HTTP Example
my_lambda_function = MasterServer(Storage('dynamodb'), Transport('http'), Headers())


print("Starting...")
storage_backend = Storage('dynamodb')
transport_backend = Transport('http')
packet_headers = Headers()

print(storage_backend)
print(transport_backend)
print(packet_headers)

storage_backend.store(my_object='Hello Storage')
transport_backend.send(my_object='Hello Transport')
result = packet_headers.find_header(b'\xff\xff\xff\xffping')
print(f"Looking for wololo, found {result}")

#print(f"True? {packet_headers.match(header='wol')}")
#print(f"False? {packet_headers.match(header='lol')}")

print("Done")
