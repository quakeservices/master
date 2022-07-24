#!/usr/bin/env python
from aws_cdk import App

from deployment.constants import APP_NAME
from deployment.environments import us_west_2
from deployment.stacks.pipeline import PipelineStack

app = App()

PipelineStack(app, f"{APP_NAME}-pipeline", env=us_west_2)

app.synth()
