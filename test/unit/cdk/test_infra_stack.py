import pytest
from aws_cdk.assertions import Match, Template

from deployment.stacks import InfraStack


@pytest.mark.cdk
@pytest.mark.unit
class TestQuakeservicesInfra:
    @pytest.fixture(scope="class")
    def stack_template(self, stack_app, stack_env_us_west_2):
        return Template.from_stack(
            InfraStack(
                stack_app,
                "test-infra",
                env=stack_env_us_west_2,
            )
        )

    def test_vpc(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::EC2::VPC",
            {
                "CidrBlock": "10.0.0.0/16",
                "EnableDnsHostnames": True,
                "EnableDnsSupport": True,
                "InstanceTenancy": "default",
                "Tags": [{"Key": "Name", "Value": Match.any_value()}],
            },
        )

    def test_vpc_subnet_public(self, stack_template):
        subnets: dict[str, str] = {
            "dummy1a": "10.0.0.0/18",
            "dummy1b": "10.0.64.0/18",
            "dummy1c": "10.0.128.0/18",
        }
        for subnet, cidr in subnets.items():
            stack_template.has_resource_properties(
                "AWS::EC2::Subnet",
                {
                    "VpcId": {"Ref": Match.any_value()},
                    "AvailabilityZone": subnet,
                    "CidrBlock": cidr,
                    "MapPublicIpOnLaunch": True,
                    "Tags": [
                        {"Key": "aws-cdk:subnet-name", "Value": "quakeservices-public"},
                        {"Key": "aws-cdk:subnet-type", "Value": "Public"},
                        {
                            "Key": "Name",
                            "Value": Match.string_like_regexp(
                                "test-infra/vpc/quakeservices-publicSubnet."
                            ),
                        },
                    ],
                },
            )

    def test_vpc_subnet_public_route_table(self, stack_template):
        stack_template.resource_count_is("AWS::EC2::RouteTable", 3)
        stack_template.has_resource_properties(
            "AWS::EC2::RouteTable",
            {
                "VpcId": {"Ref": Match.any_value()},
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": Match.string_like_regexp(
                            "test-infra/vpc/quakeservices-publicSubnet."
                        ),
                    }
                ],
            },
        )

    def test_vpc_subnet_public_route_table_association(self, stack_template):
        stack_template.resource_count_is("AWS::EC2::SubnetRouteTableAssociation", 3)
        stack_template.has_resource_properties(
            "AWS::EC2::SubnetRouteTableAssociation",
            {
                "RouteTableId": {"Ref": Match.any_value()},
                "SubnetId": {"Ref": Match.any_value()},
            },
        )

    def test_vpc_subnet_public_default_route(self, stack_template):
        stack_template.resource_count_is("AWS::EC2::Route", 3)
        stack_template.has_resource_properties(
            "AWS::EC2::Route",
            {
                "RouteTableId": {"Ref": Match.any_value()},
                "DestinationCidrBlock": "0.0.0.0/0",
                "GatewayId": {"Ref": Match.any_value()},
            },
        )

    def test_vpc_internet_gateway(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::EC2::InternetGateway",
            {"Tags": [{"Key": "Name", "Value": Match.any_value()}]},
        )

    def test_vpc_gateway(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::EC2::VPCGatewayAttachment",
            {
                "VpcId": {"Ref": Match.any_value()},
                "InternetGatewayId": {"Ref": Match.any_value()},
            },
        )

    def test_ecs_cluster(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ECS::Cluster", {"ClusterName": Match.any_value()}
        )

    def test_ecs_cluster_provider(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ECS::ClusterCapacityProviderAssociations",
            {
                "CapacityProviders": ["FARGATE", "FARGATE_SPOT"],
                "Cluster": {"Ref": Match.any_value()},
                "DefaultCapacityProviderStrategy": [],
            },
        )

    def test_route53_domains(self, stack_template):
        domains = ["quake.services.", "quake2.services.", "quake3.services."]
        for domain in domains:
            stack_template.has_resource_properties(
                "AWS::Route53::HostedZone", {"Name": domain}
            )
