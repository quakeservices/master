from aws_cdk import aws_ec2 as ec2

from deployment.models.base import DeploymentBaseModel
from deployment.models.network.security import SecurityGroupRule


class PortConfiguration(DeploymentBaseModel):
    port: int
    protocol: str
