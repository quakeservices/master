#!/usr/bin/env python3

from aws_cdk import core

from web_backend_deploy.web_backend_deploy_stack import WebBackendDeployStack


app = core.App()
WebBackendDeployStack(app, "web-backend-deploy")

app.synth()
