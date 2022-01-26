#!/usr/bin/env python3
import os

from aws_cdk import core

from deploy.deploy_stack import WebBackendDeployStack

env = {
    "account": os.getenv("AWS_ACCOUNT", os.getenv("CDK_DEFAULT_ACCOUNT", "")),
    "region": os.getenv("AWS_DEFAULT_REGION", os.getenv("CDK_DEFAULT_REGION", "")),
}


app = core.App()
WebBackendDeployStack(app, "web-backend-deploy", env=env)

app.synth()
