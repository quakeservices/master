import boto3


class Storage(object):
    def __new__(self, backend):
        if backend is 'dynamodb':
            return DynamoDB()
        elif backend is 'postgresql':
            return PostgreSQL()
        else:
            return MockStorage()


class DynamoDB():
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('q2m')

    def store(self, my_object):
        print(f"From DynamoDB: {my_object}")
        print(self.dynamodb)
        print(self.table)


class PostgreSQL():
    pass


class MockStorage():
    pass
