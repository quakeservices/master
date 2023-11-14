from dataclasses import dataclass

from aws_cdk import RemovalPolicy
from aws_cdk import aws_ec2 as ec2


@dataclass
class SecurityGroupRule:
    peer: ec2.IPeer
    connection: ec2.Port
    description: str = ""


@dataclass
class SecurityGroupConfig:
    name: str
    vpc: ec2.Vpc
    description: str = ""
    allow_all_ipv6_outbound: bool = False
    allow_all_outbound: bool = False
    disable_inline_rules: bool = False
    ingress: list[SecurityGroupRule] = []
    egress: list[SecurityGroupRule] = []
    removal_policy: RemovalPolicy = RemovalPolicy.DESTROY
