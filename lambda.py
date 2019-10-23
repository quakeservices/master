import json
from storage.model import Server


def list_servers():
    return Server.scan()

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps(list_servers())
    }
