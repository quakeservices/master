#!/usr/bin/env python3
import os

from aws_cdk import App, Environment

from stacks.infra import InfraStack
from stacks.master import MasterStack
from stacks.web_backend import WebBackendStack
from stacks.web_frontend import WebFrontendStack

from .constants import APP_NAME

default_account: str = os.getenv(
    "AWS_ACCOUNT", os.getenv("CDK_DEFAULT_ACCOUNT", "123456789012")
)
default_region: str = "us-west-2"
us_west_2 = Environment(account=default_account, region=default_region)
us_east_1 = Environment(account=default_account, region="us-east-1")


app = App()

InfraStack(app, f"{APP_NAME}-infra", env=us_west_2)
MasterStack(app, f"{APP_NAME}-master", env=us_west_2)
WebBackendStack(app, f"{APP_NAME}-backend", env=us_west_2)
WebFrontendStack(app, f"{APP_NAME}-frontend", env=us_east_1)

app.synth()
