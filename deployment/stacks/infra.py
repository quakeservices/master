from typing import Any

from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from deployment.constants import APP_NAME, DOMAINS, RECORDS
from deployment.parts.base_stack import BaseStack
from deployment.parts.dns.record import Record, RecordBuilder


class InfraStack(BaseStack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._create_vpc(
            name=APP_NAME,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"{APP_NAME}-public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                )
            ],
        )
        self._create_ecs_cluster(name=APP_NAME)
        self._create_zones(domains=DOMAINS)
        self._create_records()

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
