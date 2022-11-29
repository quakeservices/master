# pylint: disable=protected-access

import pytest

from master.protocols import ProtocolResponse
from master.server.handlers.master import MasterHandler


@pytest.mark.master_handler
@pytest.mark.unit_test
class TestMasterHandler:
    @pytest.mark.parametrize(
        "address,expected",
        [
            ("1.0.0.1:80", b"\x01\x00\x00\x01\x00P"),
            ("192.168.1.1:27910", b"\xc0\xa8\x01\x01m\x06"),
            ("192.168.1.1:27920", b"\xc0\xa8\x01\x01m\x10"),
            ("192.168.2.1:27910", b"\xc0\xa8\x02\x01m\x06"),
            ("192.168.100.100:27910", b"\xc0\xa8ddm\x06"),
            ("255.255.255.255:65535", b"\xff\xff\xff\xff\xff\xff"),
        ],
    )
    def test_pack_address(self, address: str, expected: bytes) -> None:
        assert expected == MasterHandler._pack_address(address)

    @pytest.mark.parametrize(
        "response,header,separator,expected",
        [
            ([b"hello", b"world"], None, b"", b"helloworld"),
            (
                [b"hello", b"world"],
                b"\xff",
                b"",
                b"\xffhelloworld",
            ),
            ([b"hello", b"world"], None, b" ", b"hello world"),
            ([b"hello", b"world"], b"\xff", b" ", b"\xffhello world"),
        ],
    )
    def test_create_response(
        self,
        response: list[bytes],
        header: bytes | None,
        separator: bytes,
        expected: bytes,
    ) -> None:
        assert expected == MasterHandler._create_response(response, header, separator)

    @pytest.mark.parametrize(
        "req,expected",
        [
            (
                ProtocolResponse(
                    game="testing",
                    request_type="any",
                    response_class="ping",
                    response=b"\xff\xff\xff\xffack",
                ),
                b"\xff\xff\xff\xffack",
            ),
            (
                ProtocolResponse(
                    game="testing",
                    request_type="any",
                    response_class="ping",
                    response=None,
                ),
                None,
            ),
        ],
    )
    def test_handle_generic_request(
        self, req: ProtocolResponse, expected: bytes | None
    ) -> None:
        assert expected == MasterHandler._handle_generic_request(req)
