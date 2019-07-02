import boto3


class Storage(object):
  def __init__(self):
    self.client = boto3.client('dynamodb')

  def get_server(self, server):
    pass

  def list_servers(self):
    pass

  def create_server(self, server):
    pass

  def delete_server(self, server):
    pass

  def update_server(self, server):
    pass
