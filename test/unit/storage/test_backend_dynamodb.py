# pylint: disable=protected-access
import os

import pytest
from moto import mock_dynamodb

from master.storage.models.server import Server


# mypy: allow-untyped-defs
@pytest.mark.storage_dynamodb
class TestDynamodbBackend:
    table_name: str = "testing"
    region_name: str = "us-west-2"

    @pytest.fixture(scope="class")
    def storage(self):
        with mock_dynamodb():
            # Import storage module after the mock has been initialised
            # pylint: disable=import-outside-toplevel
            from boto3.session import Session
            from moto.core import patch_resource

            from master.storage import storage

            storage_class = storage("dynamodb")

            session: Session = Session(
                aws_access_key_id="testing",
                aws_secret_access_key="testing",
                aws_session_token="testing",
                region_name=self.region_name,
            )

            resource = storage_class._create_service_resource(self.region_name, session)
            patch_resource(resource)
            storage_class._create_table(resource, self.table_name)

            storage_instance = storage_class(
                table_name=self.table_name, region=self.region_name, session=session
            )

            yield storage_instance

    @pytest.fixture(scope="class")
    def server(self) -> Server:
        return Server(
            address="127.0.0.1:27900",
            active=True,
            game="test-game",
            details={"test-detail": "test-value"},
            players=[{"name": "test-player", "ping": 4, "score": 10}],
        )

    def test_update_server(self, storage, server) -> None:
        result = storage.update_server(server)
        assert result

    def test_create_server(self, storage, server) -> None:
        result = storage.create_server(server)
        assert result

    def test_get_server(self, storage, server) -> None:
        result = storage.get_server(address="127.0.0.1:27900", game="test-game")
        assert result is not None
        assert result.address == server.address

    def test_get_server_none(self, storage, server) -> None:
        result = storage.get_server(address="127.0.0.2:27900", game="test-game")
        assert result is None

    def test_get_servers(self, storage, server):
        expected_result = [server]
        actual_result = storage.get_servers(game="test-game")
        assert actual_result == expected_result
