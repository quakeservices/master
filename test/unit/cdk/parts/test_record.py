# pylint: disable=protected-access
from test.unit.cdk.helpers.aws import AWSHelper
from typing import Callable

import pytest
from aws_cdk import Stack
from aws_cdk import aws_route53 as route53
from aws_cdk.assertions import Match, Template

from deployment.parts.dns.record import Record


@pytest.mark.cdk
@pytest.mark.unit
class TestRecord:
    @pytest.mark.parametrize(
        "domain,record_type,record_name,record_target",
        [
            pytest.param(
                "example.com",
                route53.RecordType.A,
                "test",
                route53.RecordTarget(values=["192.168.1.1"]),
                id="RecordTypeA",
            )
        ],
    )
    def test_record(
        self,
        domain: str,
        record_type: route53.RecordType,
        record_name: str,
        record_target: route53.RecordTarget,
        stack: Stack,
        zone: Callable[[Stack, str], route53.IHostedZone],
    ) -> None:
        Record(
            stack, zone(stack, domain), domain, record_type, record_name, record_target
        )

        template: Template = Template.from_stack(stack)

        assert template.resource_count_is("AWS::Route53::RecordSet", 1)
        assert template.resource_count_is("Custom::DeleteExistingRecordSet", 1)
        assert template.has_resource_properties(
            "AWS::Route53::RecordSet",
            {
                "HostedZoneId": {
                    "Ref": Match.string_like_regexp(
                        AWSHelper.format_string_for_aws(f"test{domain}*")
                    )
                },
                "Name": f"{record_name}.{domain}.",
                "ResourceRecords": record_target.values,
                "TTL": "1800",
                "Type": record_type.value,
            },
        )
