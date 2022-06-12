"""
Bare implementation of ProxyProtocolV2
This is not, and probably won't be, a full implementation.
Just enough to get things working
"""
import logging
import struct


class ProxyProtocol:
    header_format: str = ">12sccH"
    header_length: int = 16
    signature: bytes = b"\r\n\r\n\x00\r\nQUIT\n"

    @classmethod
    def parse_data(cls, data: bytes) -> bytes:
        parsed_data: bytes

        header_raw: bytes = data[: cls.header_length]
        header: tuple = struct.unpack(cls.header_format, header_raw)

        signature: bytes = header[0]
        if signature == cls.signature:
            logging.debug(
                f"{cls.__class__.__name__ } - Found proxy protocol signature."
            )
            address_length: int = header[3]
            total_length: int = cls.header_length + address_length
            parsed_data = data[total_length:]
        else:
            logging.debug(
                f"{cls.__class__.__name__ } - Did not find proxy protocol signature."
            )
            parsed_data = data

        return parsed_data
