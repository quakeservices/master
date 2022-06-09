#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from stacks.master import MasterStack
from stacks.web_backend import WebBackendStack

default_account = os.getenv("AWS_ACCOUNT", os.getenv("CDK_DEFAULT_ACCOUNT", "ap-southeast-2"))
default_region = os.getenv("AWS_DEFAULT_REGION", os.getenv("CDK_DEFAULT_REGION", "ap-southeast-2"))
env = cdk.Environment(account=default_account, region=default_region)


if __name__ == "__main__":
    app = cdk.App()

    MasterStack(app, "master-server", env=env)
    WebBackendStack(app, "master-web-backend", env=env)

    app.synth()
