import boto3

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Storage(object):
    def __new__(self, backend):
        if backend is 'dynamodb':
            return DynamoDB()
        elif backend is 'postgresql':
            return PostgreSQL()
        else:
            return MockStorage()


class DynamoDB(object):
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('q2m')

    def store(self, my_object):
        print(f"From DynamoDB: {my_object}")
        print(self.dynamodb)
        print(self.table)


class PostgreSQL(object):
    def __init__(self):
        self.engine = self.create_db_conn()
        self.session = self.create_db_session()


    def get_or_create(self, model, **kwargs):
        instance = self.session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = model(**kwargs)
            self.session.add(instance)
            self.session.commit()
            return instance


    def create_db_conn(self):
        provider = os.envion.get('DB_PROVIDER')
        username = os.envion.get('DB_USERNAME')
        password = os.envion.get('DB_PASSWORD')
        database = os.envion.get('DB_DATABASE')
        host = os.envion.get('DB_HOST')
        port = os.envion.get('DB_PORT')
        dbstring = f"{provider}://{username}:{password}@{host}:{port}/{database}"
        engine = create_engine(dbstring)

        return engine


    def create_db_session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()


class MockStorage(object):
    pass
