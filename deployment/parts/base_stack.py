from typing import Any

from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_route53 as route53
from constructs import Construct


class BaseStack(Stack):
    vpc: ec2.IVpc | None = None
    cluster: ecs.ICluster | None = None
    zones: dict[str, route53.IHostedZone] = {}
    default_removal_policy = RemovalPolicy.DESTROY

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

    def _get_vpc(self, name: str, resource_name: str = "vpc") -> ec2.IVpc:
        if self.vpc:
            return self.vpc

        return ec2.Vpc.from_lookup(self, resource_name, vpc_name=name)

    def _get_zone(
        self, name: str, resource_name: str = "domain"
    ) -> route53.IHostedZone:
        if self.zones:
            return self.zones[name]

        return route53.HostedZone.from_lookup(self, resource_name, domain_name=name)

    def _get_ecs_cluster(
        self,
        name: str,
        vpc: ec2.IVpc | None = None,
        security_groups: list | None = None,
        resource_name: str = "cluster",
    ) -> ecs.ICluster:
        if self.cluster:
            return self.cluster

        if security_groups is None:
            security_groups = []

        if vpc is None and self.vpc is not None:
            vpc = self.vpc

        return ecs.Cluster.from_cluster_attributes(
            self,
            resource_name,
            vpc=vpc,
            cluster_name=name,
            security_groups=security_groups,
        )

    def _create_vpc(
        self,
        name: str,
        subnet_configuration: list[ec2.SubnetConfiguration] | None,
        resource_name: str = "vpc",
    ) -> ec2.Vpc:
        if subnet_configuration is None:
            subnet_configuration = []

        self.vpc = ec2.Vpc(
            self,
            resource_name,
            vpc_name=name,
            subnet_configuration=subnet_configuration,
        )
        self.vpc.apply_removal_policy(self.default_removal_policy)
        return self.vpc

    def _create_ecs_cluster(self, name: str, vpc: ec2.IVpc | None) -> ecs.Cluster:
        if vpc is None and self.vpc is not None:
            vpc = self.vpc

        self.cluster = ecs.Cluster(
            self,
            "cluster",
            vpc=vpc,
            cluster_name=name,
            enable_fargate_capacity_providers=True,
        )
        self.cluster.apply_removal_policy(self.default_removal_policy)
        return self.cluster

    def _create_zones(self: domains: list[str] | None = None) -> dict[str, Zone]:
        self.zones = {domain: Zone(self, domain) for domain in DOMAINS}
        return self.zones
