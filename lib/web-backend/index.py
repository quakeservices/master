#!/usr/bin/env python
import json

from storage.backends import DynamoDbStorage as Storage

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "https://www.quake.services",
    "Vary": "Origin",
}

RESPONSE_200 = {"statusCode": 200, "headers": HEADERS}


def server_list(storage):
    server_list = list()
    for server in storage.list_servers():
        status = json.loads(server.status)
        server_list.append(
            dict(
                address=server.address,
                hostname=status.get("hostname", "unknown"),
                gametype=status.get("gamename", "baseq2"),
                mapname=status.get("mapname", "unknown"),
                players=server.player_count,
                maxplayers=status.get("maxclients", "-1"),
                password=status.get("needpass", "-1"),
                country=server.country_code,
            )
        )

    response = RESPONSE_200
    response["body"] = json.dumps(server_list)
    return response


def server_info(storage, server_id):
    # get_server_obj expects a GameServer object.
    # get_server only returns True/False
    # TODO: Fix Storage module to work with the below use case
    server_obj = storage.get_server_obj(server_id)

    status = json.loads(server_obj.status)
    players = json.loads(server_obj.players)
    server_info = {"status": status, "players": players}

    response = RESPONSE_200
    response["body"] = json.dumps(server_info)
    return response


def handler(event, context):
    # TODO: Add basic routing
    # /servers = return all active servers
    # /server/ = return all information about server
    storage = Storage()
    return server_list(storage)


if __name__ == "__main__":
    print(handler("", ""))
