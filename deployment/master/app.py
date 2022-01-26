#!/usr/bin/env python3
import os
import boto3

from aws_cdk import core as cdk

from master_deploy.master_deploy_stack import MasterDeployStack

env = {
    "account": os.getenv("AWS_ACCOUNT", os.getenv("CDK_DEFAULT_ACCOUNT", "")),
    "region": os.getenv("AWS_DEFAULT_REGION", os.getenv("CDK_DEFAULT_REGION", "")),
}

app = cdk.App()

MasterDeployStack(app, "master-deploy", env=env)

app.synth()
