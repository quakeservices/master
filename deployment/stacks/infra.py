from typing import Any

from aws_cdk import Annotations, RemovalPolicy, Stack
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_route53 as route53
from constructs import Construct

from deployment.constants import *
from deployment.types import Record


class InfraStack(Stack):
    zones: dict[str, route53.IHostedZone] = {}

    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = self._create_vpc()
        self._create_ecr_repository()
        self._create_ecs_cluster()
        self._create_zones()
        self._create_records()

    def _create_vpc(self) -> ec2.Vpc:
        return ec2.Vpc(
            self,
            "vpc",
            vpc_name=APP_NAME,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"{APP_NAME}-public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                )
            ],
        )

    def _create_ecs_cluster(self) -> None:
        self.cluster = ecs.Cluster(
            self,
            "cluster",
            vpc=self.vpc,
            cluster_name=APP_NAME,
            enable_fargate_capacity_providers=True,
        )

    def _create_ecr_repository(self) -> None:
        lifecycle_rules = [
            ecr.LifecycleRule(tag_prefix_list=["master"], max_image_count=5)
        ]
        ecr.Repository(
            self,
            "repository",
            repository_name=APP_NAME,
            removal_policy=RemovalPolicy.DESTROY,
            lifecycle_rules=lifecycle_rules,
        )

    def _create_zones(self) -> None:
        for domain in DOMAINS:
            zone = route53.PublicHostedZone(self, domain, zone_name=domain)
            zone.apply_removal_policy(RemovalPolicy.DESTROY)
            self.zones[domain] = zone

    def _create_records(self) -> None:
        for domain, records in RECORDS.items():
            if "TXT" in records:
                self._create_txt_records(domain, records["TXT"])
            if "CNAME" in records:
                self._create_cname_records(domain, records["CNAME"])
            if "A" in records:
                self._create_a_records(domain, records["A"])

    def _create_txt_records(self, domain: str, records: list[Record]) -> None:
        for record in records:
            key: str = self._list_to_str(record["key"])
            entry = route53.TxtRecord(
                self,
                f"{domain}-{key}-txt",
                zone=self.zones[domain],
                record_name=key,
                values=record["values"],
            )
            entry.apply_removal_policy(RemovalPolicy.DESTROY)

    def _create_cname_records(self, domain: str, records: list[Record]) -> None:
        for record in records:
            key: str = self._list_to_str(record["key"])
            for value in record["values"]:
                entry = route53.CnameRecord(
                    self,
                    f"{domain}-{key}-cname",
                    zone=self.zones[domain],
                    record_name=key,
                    domain_name=value,
                )
                entry.apply_removal_policy(RemovalPolicy.DESTROY)

    def _create_a_records(self, domain: str, records: list[Record]) -> None:
        for record in records:
            key: str = self._list_to_str(record["key"])
            value: str = self._list_to_str(record["values"])

            target: route53.RecordTarget = route53.RecordTarget.from_ip_addresses(value)
            entry = route53.ARecord(
                self,
                f"{domain}-{key}-a",
                zone=self.zones[domain],
                record_name=key,
                target=target,
            )
            entry.apply_removal_policy(RemovalPolicy.DESTROY)

    @staticmethod
    def _list_to_str(value: str | list[str]) -> str:
        if isinstance(value, list):
            return value.pop()

        return value
