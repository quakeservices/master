# pylint: disable=protected-access
from test.unit.cdk.helpers.aws import AWSHelper
from typing import Any, Callable

import pytest
from aws_cdk import Stack
from aws_cdk import aws_route53 as route53
from aws_cdk.assertions import Match, Template

from deployment.parts.dns.record import Record, RecordBuilder


@pytest.mark.cdk
@pytest.mark.unit
class TestRecordBuilder:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            pytest.param("example.com", False, id="String"),
            pytest.param(["example.com"], True, id="ListStr"),
            pytest.param(1, False, id="Int"),
        ],
    )
    def test_is_list(self, test_input: Any, expected: bool) -> None:
        assert expected == RecordBuilder._is_list(test_input)

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            pytest.param("example.com", False, id="String"),
            pytest.param(["example.com"], True, id="ListStr"),
            pytest.param([1, 2, 3], False, id="ListInt"),
        ],
    )
    def test_is_list_of_strings(self, test_input: Any, expected: bool) -> None:
        assert expected == RecordBuilder._is_list_of_strings(test_input)

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            pytest.param(
                ["192.168.1.1"],
                route53.RecordTarget(values=["192.168.1.1"]),
                id="ListStringToRecordTarget",
            ),
            pytest.param(
                route53.RecordTarget(values=["192.168.1.1"]),
                route53.RecordTarget(values=["192.168.1.1"]),
                id="RecordTargetUnchanged",
            ),
            pytest.param("192.168.1.1", None, id="StringToNone"),
        ],
    )
    def test_target_to_object(
        self,
        test_input: list[str] | route53.RecordTarget,
        expected: route53.RecordTarget | None,
    ) -> None:
        result: route53.RecordTarget | None = RecordBuilder._target_to_object(
            test_input
        )
        if isinstance(test_input, list):
            assert result is not None
            assert result.values == test_input

        if isinstance(test_input, route53.RecordTarget):
            assert result.values == expected.values

        if expected is None:
            assert result is None

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            pytest.param("A", route53.RecordType.A, id="StringAToObject"),
            pytest.param("CNAME", route53.RecordType.CNAME, id="StringCNAMEToObject"),
            pytest.param("TXT", route53.RecordType.TXT, id="StringTXTToObject"),
            pytest.param(
                route53.RecordType.A, route53.RecordType.A, id="ObjectAUnchanged"
            ),
            pytest.param(
                route53.RecordType.CNAME,
                route53.RecordType.CNAME,
                id="ObjectCNAMEUnchanged",
            ),
            pytest.param("Nope", None, id="UnknownStringToNone"),
        ],
    )
    def test_type_to_object(
        self, test_input: str | route53.RecordType, expected: route53.RecordType | None
    ) -> None:
        assert expected == RecordBuilder._type_to_object(test_input)

    @pytest.mark.skip("Broken")
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
    def test_create_record(
        self,
        domain: str,
        record_type: str | route53.RecordType,
        record_name: str,
        record_target: list[str] | route53.RecordTarget,
        stack: Stack,
        zone: Callable[[Stack, str], route53.IHostedZone],
    ) -> None:
        zones: dict[str, route53.IHostedZone] = {domain: zone(stack, domain)}
        builder: RecordBuilder = RecordBuilder(stack, "builder", zones)
        builder.create_record(domain, record_type, record_name, record_target)

        # Convert to objects for easier comparison
        record_target = RecordBuilder._target_to_object(record_target)
        record_type = RecordBuilder._type_to_object(record_type)

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
                "Type": record_type.name,
            },
        )
