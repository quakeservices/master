#!/usr/bin/env python3
import os

from aws_cdk import core as cdk
from stacks.master import MasterStack
from stacks.web_backend import WebBackendStack

env = {
    "account": os.getenv("AWS_ACCOUNT", os.getenv("CDK_DEFAULT_ACCOUNT", "")),
    "region": os.getenv("AWS_DEFAULT_REGION", os.getenv("CDK_DEFAULT_REGION", "")),
}


app = cdk.App()

MasterStack(app, "master-server", env=env)
WebBackendStack(app, "master-web-backend", env=env)

app.synth()
