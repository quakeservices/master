import os
from datetime import datetime

from pynamodb.attributes import (BooleanAttribute, JSONAttribute,
                                 NumberAttribute, UnicodeAttribute,
                                 UTCDateTimeAttribute)
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model


class PynamoServerIndex(GlobalSecondaryIndex):
    class Meta:
        if os.getenv("STAGE", "PRODUCTION") == "TESTING":
            host = "http://dynamodb:8000"
        index_name = "server_index"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()
        region = "us-west-2"

    address = UnicodeAttribute(hash_key=True)
    game = UnicodeAttribute(range_key=True)


class PynamoServer(Model):
    class Meta:
        if os.getenv("STAGE", "PRODUCTION") == "TESTING":
            host = "http://dynamodb:8000"
        table_name = "server"
        billing_mode = "PAY_PER_REQUEST"
        region = "us-west-2"

    server_index = PynamoServerIndex()

    address = UnicodeAttribute(hash_key=True)
    game = UnicodeAttribute()

    protocol = NumberAttribute(default=0)

    status = JSONAttribute()
    players = JSONAttribute()
    player_count = NumberAttribute(default=0)

    active = BooleanAttribute(default=True)
    scraped = BooleanAttribute(default=False)

    first_seen = UTCDateTimeAttribute(default=datetime.utcnow())
    last_seen = UTCDateTimeAttribute(default=datetime.utcnow())

    country_code = UnicodeAttribute(default="ZZ")
