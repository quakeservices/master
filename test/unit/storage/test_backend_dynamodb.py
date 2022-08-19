import os

import boto3
import pytest
from moto import mock_dynamodb

from master.storage.models.server import Server


class TestDynamodbBackend:
    @pytest.fixture(scope="class")
    def aws_credentials(self) -> None:
        """Mocked AWS Credentials for moto."""
        os.environ["AWS_ACCESS_KEY_ID"] = "testing"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
        os.environ["AWS_SECURITY_TOKEN"] = "testing"
        os.environ["AWS_SESSION_TOKEN"] = "testing"
        os.environ["AWS_DEFAULT_REGION"] = "us-west-2"

    @pytest.fixture(scope="class")
    def dynamodb(self, aws_credentials):
        with mock_dynamodb():
            yield boto3.client("dynamodb", region_name="us-west-2")

    @pytest.fixture(scope="class")
    def table(self, dynamodb) -> None:
        dynamodb.create_table(
            TableName="quakeservices",
            BillingMode="PAY_PER_REQUEST",
            KeySchema=[
                {"AttributeName": "address", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "address", "AttributeType": "S"},
            ],
        )

    @pytest.fixture(scope="class")
    def server(self) -> Server:
        return Server(
            address="127.0.0.1:27900",
            active=True,
            game="test-game",
            details={"test-detail": "test-value"},
            players=[{"name": "test-player", "ping": 4, "score": 10}],
        )

    @pytest.fixture(scope="class")
    def storage(self, dynamodb):
        from master.storage.backends.dynamodb import DynamoDbStorage

        return DynamoDbStorage()

    @pytest.mark.skip(reason="TODO: Fix dynamodb mock")
    def test_update_server(self, storage, table, server) -> None:
        result = storage.update_server(server)
        assert result

    @pytest.mark.skip(reason="TODO: Fix dynamodb mock")
    def test_create_server(self, storage, table, server) -> None:
        result = storage.create_server(server)
        assert result

    @pytest.mark.skip(reason="TODO: Fix dynamodb mock")
    def test_get_server(self, storage, table, server) -> None:
        result = storage.get_server(address="127.0.0.1:27900", game="test-game")
        assert result is not None
        assert result.address == server.address

    @pytest.mark.skip(reason="TODO: Fix dynamodb mock")
    def test_get_servers(self, storage, table, server):
        expected_result = [server]
        actual_result = storage.get_servers(game="test-game")
        assert actual_result == expected_result
