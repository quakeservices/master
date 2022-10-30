import logging
from decimal import Decimal
from typing import Any, Mapping, Optional, Sequence, Union

from boto3.dynamodb.conditions import Attr, Key
from boto3.session import Session
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
from mypy_boto3_dynamodb.type_defs import (
    GetItemOutputTableTypeDef,
    QueryOutputTableTypeDef,
    ScanOutputTableTypeDef,
    UpdateItemOutputTableTypeDef,
)

from master.constants import APP_NAME, DEFAULT_REGION, DEPLOYMENT_ENVIRONMENT
from master.storage.base import BaseStorage
from master.storage.models.server import Server

Item = dict[
    str,
    Union[
        bytes,
        bytearray,
        str,
        int,
        Decimal,
        bool,
        set[int],
        set[Decimal],
        set[str],
        set[bytes],
        set[bytearray],
        Sequence[Any],
        Mapping[str, Any],
        None,
    ],
]

DEFAULT_SESSION = Session()
DEFAULT_TABLE_NAME = f"{APP_NAME}-{DEPLOYMENT_ENVIRONMENT}"


class DynamoDbStorage(BaseStorage):
    table: Table
    dynamodb: DynamoDBServiceResource
    primary_key: str = "address"

    def __init__(
        self,
        table_name: str = DEFAULT_TABLE_NAME,
        region: str = DEFAULT_REGION,
        session: Optional[Session] = DEFAULT_SESSION,
    ):
        self.dynamodb = self._create_service_resource(region, session)
        self.table = self._get_table(self.dynamodb, table_name)

    @classmethod
    def initialise(cls) -> None:
        if DEPLOYMENT_ENVIRONMENT == "dev":
            resource: DynamoDBServiceResource = cls._create_service_resource()
            cls._create_table(resource)

    @staticmethod
    def _create_service_resource(
        region: str = DEFAULT_REGION, session: Session = DEFAULT_SESSION
    ) -> DynamoDBServiceResource:

        resource: DynamoDBServiceResource

        if DEPLOYMENT_ENVIRONMENT == "dev":
            # We're in development so use dynamodb-local
            resource = session.resource(
                "dynamodb",
                region_name=region,
                endpoint_url="http://dynamodb-local:8000",
            )
        else:
            # We're in production or (unit) testing so use real endpoint
            # dynamodb client will be mocked out in unit testing
            resource = session.resource("dynamodb", region_name=region)

        return resource

    @classmethod
    def _create_table(
        cls, resource: DynamoDBServiceResource, table_name: str = DEFAULT_TABLE_NAME
    ) -> None:
        try:
            logging.debug("Creating table %s", table_name)
            resource.create_table(
                TableName=table_name,
                BillingMode="PAY_PER_REQUEST",
                KeySchema=[
                    {"AttributeName": cls.primary_key, "KeyType": "HASH"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": cls.primary_key, "AttributeType": "S"},
                ],
            )
        except resource.meta.client.exceptions.ResourceInUseException:
            logging.debug("Table already exists, skipping creation.")
        else:
            logging.debug("Table created.")

    @classmethod
    def _get_table(
        cls, resource: DynamoDBServiceResource, table_name: str = DEFAULT_TABLE_NAME
    ) -> Table:
        return resource.Table(table_name)

    def create_server(self, server: Server) -> bool:
        return self.update_server(server)

    def get_server(self, address: str, game: Optional[str] = None) -> Optional[Server]:
        server: Optional[Server] = None
        result: Optional[Item] = self._query_item(address, game)

        if result:
            server = Server.parse_obj(result)

        return server

    def get_servers(self, game: Optional[str] = None) -> list[Server]:
        servers: list = []

        result = self._scan(game)
        for server in result:
            servers.append(Server.parse_obj(server))

        return servers

    def _scan(self, game: Optional[str] = None) -> list[Item]:
        response: ScanOutputTableTypeDef
        if game:
            response = self.table.scan(
                FilterExpression=Attr("game").eq(game) & Attr("active").eq(True)
            )
        else:
            response = self.table.scan(FilterExpression=Attr("active").eq(True))

        items = response["Items"]
        return items

    def update_server(self, server: Server) -> bool:
        return self._update_item(server)

    def _update_item(self, server: Server) -> bool:
        update_expression: str = "SET active=:a, game=:g, details=:d, players=:p"
        expression_attribute_values: dict[str, Any] = {
            ":a": server.active,
            ":g": server.game,
            ":d": server.details,
            ":p": server.players,
        }
        result: UpdateItemOutputTableTypeDef = self.table.update_item(
            Key={self.primary_key: server.address},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW",
        )

        # The Attributes map is only present if ReturnValues was specified as
        # something other than NONE in the request.
        if "Attributes" in result:
            return True

        return False

    def _query_item(self, address: str, game: str, limit: int = 1) -> Optional[Item]:
        items: Optional[list[Item]] = None
        try:
            result: QueryOutputTableTypeDef = self.table.query(
                Limit=limit,
                ConsistentRead=True,
                ReturnConsumedCapacity="NONE",
                KeyConditionExpression=Key(self.primary_key).eq(address),
                FilterExpression=Attr("game").eq(game),
            )
        except (
            self.dynamodb.meta.client.exceptions.InternalServerError,
            self.dynamodb.meta.client.exceptions.ProvisionedThroughputExceededException,
            self.dynamodb.meta.client.exceptions.RequestLimitExceeded,
            self.dynamodb.meta.client.exceptions.ResourceNotFoundException,
        ) as exception:
            self._log_exception("_query_item", exception)
        else:
            items = result.get("Items", None)
            if items:
                return items.pop()
        return None

    @staticmethod
    def _log_exception(method: str, exception: Any) -> None:
        logging.error("Method %s caught exception: ", method)
        logging.error(exception.message)

    def _get_item(self, address: str) -> Optional[Item]:
        """
        Unused
        """
        try:
            response: GetItemOutputTableTypeDef = self.table.get_item(
                Key={"address": address}
            )
        except (
            self.dynamodb.meta.client.exceptions.InternalServerError,
            self.dynamodb.meta.client.exceptions.ProvisionedThroughputExceededException,
            self.dynamodb.meta.client.exceptions.RequestLimitExceeded,
            self.dynamodb.meta.client.exceptions.ResourceNotFoundException,
        ) as exception:
            self._log_exception("_get_item", exception)
        else:
            return response["Item"]

        return None
