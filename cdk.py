#!/usr/bin/env python
from aws_cdk import App

from deployment.constants import APP_NAME
from deployment.environments import us_west_2
from deployment.stacks.pipeline import PipelineStack

app = App()

PipelineStack(app, f"{APP_NAME}-pipeline", env=us_west_2)
# InfraStack(app, f"{APP_NAME}-infra", env=us_west_2)
# MasterStack(app, f"{APP_NAME}-master", env=us_west_2)
# WebBackendStack(app, f"{APP_NAME}-backend", env=us_west_2)
# WebFrontendStack(app, f"{APP_NAME}-frontend", env=us_east_1)

app.synth()