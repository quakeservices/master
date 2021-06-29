#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from master_deploy.master_deploy_stack import MasterDeployStack
from master_deploy.xray_deploy_stack import XrayDeployStack

env = {
    "account": os.getenv("AWS_ACCOUNT", os.getenv("CDK_DEFAULT_ACCOUNT", "")),
    "region": os.getenv("AWS_DEFAULT_REGION", os.getenv("CDK_DEFAULT_REGION", "")),
}

vpc_id = "vpc-0051b8b7bdff9a7d0"

app = cdk.App()

MasterDeployStack(app, "master-deploy", vpc_id, env=env)
XrayDeployStack(app, "xray-deploy", vpc_id, env=env)

app.synth()
