import struct


class ProxyProtocol:
    """
    Bare implementation of ProxyProtocolV2
    This is not, and probably won't be, a full implementation.
    Just enough to get things working
    """

    header_format: str = ">12sccH"
    header_length: int = 16
    signature: bytes = b"\r\n\r\n\x00\r\nQUIT\n"

    @classmethod
    def parse_request(cls, request: bytes) -> bytes:
        parsed_request: bytes = b""

        header_raw: bytes = request[: cls.header_length]
        header: tuple = struct.unpack(cls.header_format, header_raw)

        signature: bytes = header[0]
        if signature == cls.signature:
            # Found proxy protocol signature
            address_length: int = header[3]
            total_length: int = cls.header_length + address_length
            parsed_request = request[total_length:]
        else:
            # Did not find proxy protocol signature
            parsed_request = request

        return parsed_request
