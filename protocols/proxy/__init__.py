"""
Bare implementation of ProxyProtocolV2
This is not, and probably won't be, a full implementation.
Just enough to get things working
"""
import struct
import logging


class ProxyProtocol:
    def __init__(self):
        pass

    @staticmethod
    def parse_data(data: bytes) -> bytes:
        # pylint: disable=undefined-variable
        header_format = ">12sccH"
        header_length = 16
        header_raw = data[:header_length]

        header = struct.unpack(header_format, header_raw)

        signature = header[0]
        if signature == b"\r\n\r\n\x00\r\nQUIT\n":
            logging.debug(f"{__class__.__name__ } - Found proxy protocol signature.")
            address_length = header[3]
            total_length = header_length + address_length
            parsed_data = data[total_length:]
        else:
            logging.debug(
                f"{__class__.__name__ } - Did not find proxy protocol signature."
            )
            parsed_data = data

        return parsed_data
