from master.storage.backends.dynamodb import DynamoDbStorage
from master.storage.base import BaseStorage


def storage(backend: str) -> type[BaseStorage] | None:
    match backend:
        case "dynamodb":
            return DynamoDbStorage
        case _:
            return None
