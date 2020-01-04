#!/usr/bin/env python3
import os

from aws_cdk import core

from master_deploy.master_deploy_stack import MasterDeployStack

env = {'account': os.getenv('AWS_ACCOUNT', os.getenv('CDK_DEFAULT_ACCOUNT', '')),
       'region': os.getenv('AWS_DEFAULT_REGION', os.getenv('CDK_DEFAULT_REGION', ''))}

app = core.App()
MasterDeployStack(app, "master-deploy", env=env)

app.synth()
