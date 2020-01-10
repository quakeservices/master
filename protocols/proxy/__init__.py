import stuct


class ProxyProtocol:
    def __init__(self):
        pass

    @staticmethod
    def parse_data(data):
        header_format = '>12sccH'
        header_length = 16
        header_raw = data[:header_length]

        header = struct.unpack(header_format, header_raw)

        signature = header[0]
        if signature == b'\r\n\r\n\x00\r\nQUIT\n':
            address_length = header[3]
            total_length = header_length + address_length
            parsed_data = data[total_length:]
        else:
            parsed_data = data

        return parsed_data
