#!/usr/bin/env python
from aws_cdk import App

from deployment.constants import APP_NAME
from deployment.environments import us_west_2
from deployment.stacks import InfraStack, MasterStack

app = App()

InfraStack(app, f"{APP_NAME}-infra", env=us_west_2)
MasterStack(app, f"{APP_NAME}-master", env=us_west_2)

app.synth()
