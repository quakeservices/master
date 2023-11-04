from constructs import Construct
from aws_cdk import aws_route53 as route53
from aws_cdk import RemovalPolicy


class Zone(route53.PublicHostedZone):
    def __init__(
        self,
        scope: Construct,
        domain: str,
        removal_policy: RemovalPolicy = RemovalPolicy.DESTROY,
    ):
        super().__init__(scope, domain, zone_name=domain)
        self.apply_removal_policy(removal_policy)
