import boto3
import logging


class Storage(object):
  def __init__(self):
    logging.debug(f"{__class__.__name__ } - Initialising storage.")
    self.client = boto3.resource('dynamodb')
    self.table = self.client.Table('master')

  def get_server(self, server):
    return self.table.get_item(
        Key={
          'ServerAddress': server.address,
          'ServerPort': server.port
          }
        )

  def list_servers(self, game):
    return self.table.scan(
        FilterExpression=Attr('game').eq(game)
    )

  def create_server(self, server):
    try:
      self.table.put_item(server)
    except:
      return False
    else:
      return True

  def update_server(self, server):
    update_expression = []
    expression_attributes = {}

    for idx, (k, v) in enumerate(server.items()):
      val = f'val{idx}'
      update_expression.append(f'SET {k} = :{val}')
      expression_attributes[f':{val}'] = v

    update_expression = ', '.join(update_expression)

    try:
      self.table.update_item(
          Key={
            'ServerAddress': server.address,
            'ServerPort': server.port
            },
          UpdateExpression=update_expression,
          ExpressionAttributeValues=expression_attributes
          )
    except:
      return False
    else: 
      return True
