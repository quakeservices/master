#!/usr/bin/env python
import json
from storage import Storage

HEADERS = {'Content-Type': 'application/json',
           'Access-Control-Allow-Origin': 'https://www.quake.services',
           'Vary': 'Origin'}

200_RESPONSE = { 'statusCode': 200,
                 'headers': HEADERS }

def server_list(storage):
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

    response = 200_RESPONSE
    response['body'] = json.dumps(server_list)
    return response

def server_info(storage, server_id):
    # get_server_obj expects a GameServer object.
    # get_server only returns True/False
    # TODO: Fix Storage module to work with the below use case
    server_obj = storage.get_server_obj(server_id):

    status = json.loads(server.status)
    players = json.loads(server.players)
    server_info = { 'status': status,
                    'players': players}

    response = 200_RESPONSE
    response['body'] = json.dumps(server_info)
    return response

def lambda_handler(event, context):
    # TODO: Add basic routing
    # /servers = return all active servers
    # /server/ = return all information about server
    storage = Storage()
    return server_list(storage)


if __name__ == '__main__':
    print(lambda_handler('', ''))
