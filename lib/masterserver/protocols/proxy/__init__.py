"""
Bare implementation of ProxyProtocolV2
This is not, and probably won't be, a full implementation.
Just enough to get things working
"""
import struct

from helpers import LoggingMixin


class ProxyProtocol(LoggingMixin):
    header_format: str = ">12sccH"
    header_length: int = 16
    signature: bytes = b"\r\n\r\n\x00\r\nQUIT\n"

    def parse_data(self, data: bytes) -> bytes:
        parsed_data: bytes

        header_raw: bytes = data[: self.header_length]
        header: tuple = struct.unpack(self.header_format, header_raw)

        signature: bytes = header[0]
        if signature == self.signature:
            self.log("Found proxy protocol signature.")
            address_length: int = header[3]
            total_length: int = self.header_length + address_length
            parsed_data = data[total_length:]
        else:
            self.log("Did not find proxy protocol signature.")
            parsed_data = data

        return parsed_data
