#!/usr/bin/env python3
import os

from aws_cdk import App, Environment

from deployment.constants import APP_NAME
from deployment.environments import us_east_1, us_west_2
from deployment.stacks.infra import InfraStack
from deployment.stacks.master import MasterStack
from deployment.stacks.pipeline import PipelineStack
from deployment.stacks.web_backend import WebBackendStack
from deployment.stacks.web_frontend import WebFrontendStack

app = App()

PipelineStack(app, f"{APP_NAME}-pipeline", env=us_west_2)
# InfraStack(app, f"{APP_NAME}-infra", env=us_west_2)
# MasterStack(app, f"{APP_NAME}-master", env=us_west_2)
# WebBackendStack(app, f"{APP_NAME}-backend", env=us_west_2)
# WebFrontendStack(app, f"{APP_NAME}-frontend", env=us_east_1)

app.synth()
