from typing import Any

from aws_cdk import Annotations, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_route53 as route53
from constructs import Construct

from deployment.constants import APP_NAME, DOMAINS, RECORDS
from deployment.parts.dns.record import Record, RecordBuilder
from deployment.parts.dns.zone import Zone


class InfraStack(Stack):
    zones: dict[str, route53.IHostedZone] = {}

    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = self._create_vpc()
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

    def _create_zones(self) -> None:
        self.zones = {domain: Zone(self, domain) for domain in DOMAINS}

    def _create_records(self) -> list[Record]:
        builder = RecordBuilder(self, "record-builder", self.zones)

        return [
            builder.create_record(
                domain,
                record_type,
                record["name"],
                record["targets"],
            )
            for domain, records_by_type in RECORDS.items()
            for record_type, record_values in records_by_type.items()
            for record in record_values
        ]
