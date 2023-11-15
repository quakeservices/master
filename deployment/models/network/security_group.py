from aws_cdk import RemovalPolicy
from aws_cdk import aws_ec2 as ec2
from pydantic import Field

from deployment.models.base import DeploymentBaseModel


class SecurityGroupRule(DeploymentBaseModel):
    peer: ec2.IPeer
    connection: ec2.Port
    description: str = ""


class SecurityGroupConfig(DeploymentBaseModel):
    name: str
    vpc: ec2.Vpc
    description: str = ""
    allow_all_ipv6_outbound: bool = False
    allow_all_outbound: bool = False
    disable_inline_rules: bool = False
    ingress: list[SecurityGroupRule] = Field(default_factory=list)
    egress: list[SecurityGroupRule] = Field(default_factory=list)
    removal_policy: RemovalPolicy = RemovalPolicy.DESTROY
