#!/usr/bin/env python
import json

from storage.backends import DynamoDbStorage as Storage

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "https://www.quake.services",
    "Vary": "Origin",
}

RESPONSE_200 = {"statusCode": 200, "headers": HEADERS}
storage = Storage()


def server_list() -> dict:
    servers: list[dict] = []
    for server in storage.get_servers():
        status = json.loads(server.status)
        servers.append(
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
    response["body"] = json.dumps(servers)
    return response


def server_info(server_id: str) -> dict:
    # get_server_obj expects a GameServer object.
    # get_server only returns True/False
    # TODO: Fix Storage module to work with the below use case
    server_obj = storage.get_server(server_id)

    status = json.loads(server_obj.status)
    players = json.loads(server_obj.players)
    info = {"status": status, "players": players}

    response = RESPONSE_200
    response["body"] = json.dumps(info)
    return response


def handler(*args):  # type: ignore
    # TODO: Add basic routing
    # /servers = return all active servers
    # /server/ = return all information about server
    return server_list()


if __name__ == "__main__":
    print(handler("", ""))
