#!/usr/bin/env python
import json
from storage import Storage


def lambda_handler(event, context):
    storage = Storage()
    server_list = list()
    for server in storage.list_servers():
        status = json.loads(server.status)
        server_list.append(dict(address = server.address,
                                hostname = status.get('hostname', 'unknown'),
                                mapname = status.get('mapname', 'unknown'),
                                players = server.player_count,
                                maxplayers = status.get('maxclients', '-1'),
                                password = status.get('needpass', '-1'),
                                country = server.country_code))

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(server_list)
    }

if __name__ == '__main__':
    print(lambda_handler('', ''))
