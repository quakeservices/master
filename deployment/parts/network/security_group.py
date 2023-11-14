from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from deployment.models.network.security_group import (
    SecurityGroupConfig,
    SecurityGroupRule,
)


class SecurityGroup(ec2.SecurityGroup):
    def __init__(self, scope: Construct, config: SecurityGroupConfig) -> None:
        super().__init__(
            scope,
            config.name,
            security_group_name=config.name,
            vpc=config.vpc,
            description=config.description,
            allow_all_outbound=config.allow_all_outbound,
            allow_all_ipv6_outbound=config.allow_all_ipv6_outbound,
            disable_inline_rules=config.disable_inline_rules,
        )
        self.apply_removal_policy(config.removal_policy)
        self._add_ingress(config.ingress)
        self._add_egress(config.egress)

    def _add_ingress(self, ingress: list[SecurityGroupRule]) -> None:
        for rule in ingress:
            self.add_ingress_rule(
                rule.peer,
                rule.connection,
                rule.description,
            )

    def _add_egress(self, egress: list[SecurityGroupRule]) -> None:
        for rule in egress:
            self.add_egress_rule(
                rule.peer,
                rule.connection,
                rule.description,
            )
