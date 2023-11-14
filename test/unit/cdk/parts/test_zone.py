import pytest
from aws_cdk import Stack
from aws_cdk.assertions import Template

from deployment.parts.dns.zone import Zone


@pytest.mark.cdk
@pytest.mark.unit
def test_zone_construct(stack: Stack) -> None:
    domain: str = "example.com"
    zone = Zone(stack, domain)
    template = Template.from_stack(stack)
    template.resource_count_is("AWS::Route53::HostedZone", 1)
    template.has_resource(
        "AWS::Route53::HostedZone",
        {
            "Properties": {"Name": f"{domain}."},
            "DeletionPolicy": "Delete",
            "UpdateReplacePolicy": "Delete",
        },
    )
