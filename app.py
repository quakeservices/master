#!/usr/bin/env python3

from aws_cdk import core

from master_deploy.master_deploy_stack import MasterDeployStack


app = core.App()
MasterDeployStack(app, "master-deploy")

app.synth()
