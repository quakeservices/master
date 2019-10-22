#!/usr/bin/env python3
from flask import Flask
from flask_pynamodb_resource import modelresource_factory

from storage.model import Server

# Ensure tables exist before serving content
def create_table():
    Server.create_table(wait=True)

# Set up Flask app
app = Flask(__name__)
app.before_first_request(create_table)

# Register auto-generated routes for the model, under the '/api/v1/server' prefix
modelresource_factory(Server).register(app, '/api/v1/server')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
