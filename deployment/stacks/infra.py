from typing import Any, Optional, Union

from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_route53 as route53
from constructs import Construct

from deployment.constants import APP_NAME, DEPLOYMENT_ENVIRONMENT, DOMAINS, RECORDS


class InfraStack(Stack):
    zones: dict[str, route53.IHostedZone] = {}

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs: Any,
    ) -> None:
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
        ecs.Cluster(
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
            for record in records:
                self._create_route53_record(domain, record)

    def _create_route53_record(self, domain: str, record: dict[str, str]) -> None:
        """
        Create Route53 entries
        """
        entry: Optional[Union[route53.TxtRecord, route53.CnameRecord]] = None
        key: str = record["key"]
        match record["type"]:
            case "TXT":
                entry = route53.TxtRecord(
                    self,
                    f"{domain}-{key}-txt",
                    zone=self.zones[domain],
                    record_name=key,
                    values=[record["value"]],
                    delete_existing=True,
                )
            case "CNAME":
                entry = route53.CnameRecord(
                    self,
                    f"{domain}-{key}-cname",
                    zone=self.zones[domain],
                    record_name=key,
                    domain_name=record["value"],
                    delete_existing=True,
                )

        if entry:
            entry.apply_removal_policy(RemovalPolicy.DESTROY)
