import pytest
from aws_cdk.assertions import Match, Template

from deployment.stacks import InfraStack


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

    def test_vpcA2121C38(self, stack_template):
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

    def test_vpcquakeservicespublicSubnet1SubnetE925D692(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::EC2::Subnet",
            {
                "VpcId": {"Ref": Match.any_value()},
                "AvailabilityZone": "dummy1a",
                "CidrBlock": "10.0.0.0/18",
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

    def test_vpcquakeservicespublicSubnet1RouteTable25B6236F(self, stack_template):
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

    def test_vpcquakeservicespublicSubnet1RouteTableAssociation89B3F0E5(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::EC2::SubnetRouteTableAssociation",
            {
                "RouteTableId": {"Ref": Match.any_value()},
                "SubnetId": {"Ref": Match.any_value()},
            },
        )

    def test_vpcquakeservicespublicSubnet1DefaultRoute69AA5859(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::EC2::Route",
            {
                "RouteTableId": {"Ref": Match.any_value()},
                "DestinationCidrBlock": "0.0.0.0/0",
                "GatewayId": {"Ref": Match.any_value()},
            },
        )

    def test_vpcquakeservicespublicSubnet2Subnet63894819(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::EC2::Subnet",
            {
                "VpcId": {"Ref": Match.any_value()},
                "AvailabilityZone": "dummy1b",
                "CidrBlock": "10.0.64.0/18",
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

    def test_vpcquakeservicespublicSubnet2RouteTableA7C2A01F(self, stack_template):
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

    def test_vpcquakeservicespublicSubnet2RouteTableAssociation66A98E30(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::EC2::SubnetRouteTableAssociation",
            {
                "RouteTableId": {"Ref": Match.any_value()},
                "SubnetId": {"Ref": Match.any_value()},
            },
        )

    def test_vpcquakeservicespublicSubnet2DefaultRoute8BD66AC4(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::EC2::Route",
            {
                "RouteTableId": {"Ref": Match.any_value()},
                "DestinationCidrBlock": "0.0.0.0/0",
                "GatewayId": {"Ref": Match.any_value()},
            },
        )

    def test_vpcquakeservicespublicSubnet3SubnetACBA23E5(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::EC2::Subnet",
            {
                "VpcId": {"Ref": Match.any_value()},
                "AvailabilityZone": "dummy1c",
                "CidrBlock": "10.0.128.0/18",
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

    def test_vpcquakeservicespublicSubnet3RouteTableEC43CF57(self, stack_template):
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

    def test_vpcquakeservicespublicSubnet3RouteTableAssociation0B2EF99C(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::EC2::SubnetRouteTableAssociation",
            {
                "RouteTableId": {"Ref": Match.any_value()},
                "SubnetId": {"Ref": Match.any_value()},
            },
        )

    def test_vpcquakeservicespublicSubnet3DefaultRoute6743677A(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::EC2::Route",
            {
                "RouteTableId": {"Ref": Match.any_value()},
                "DestinationCidrBlock": "0.0.0.0/0",
                "GatewayId": {"Ref": Match.any_value()},
            },
        )

    def test_vpcIGWE57CBDCA(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::EC2::InternetGateway",
            {"Tags": [{"Key": "Name", "Value": Match.any_value()}]},
        )

    def test_vpcVPCGW7984C166(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::EC2::VPCGatewayAttachment",
            {
                "VpcId": {"Ref": Match.any_value()},
                "InternetGatewayId": {"Ref": Match.any_value()},
            },
        )

    def test_repository9F1A3F0B(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ECR::Repository",
            {
                "LifecyclePolicy": {
                    "LifecyclePolicyText": '{"rules":[{"rulePriority":1,"selection":{"tagStatus":"tagged","tagPrefixList":["master"],"countType":"imageCountMoreThan","countNumber":5},"action":{"type":"expire"}}]}'
                },
                "RepositoryName": Match.any_value(),
            },
        )

    def test_cluster611F8AFF(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ECS::Cluster", {"ClusterName": Match.any_value()}
        )

    def test_clusterA4C38409(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ECS::ClusterCapacityProviderAssociations",
            {
                "CapacityProviders": ["FARGATE", "FARGATE_SPOT"],
                "Cluster": {"Ref": Match.any_value()},
                "DefaultCapacityProviderStrategy": [],
            },
        )

    def test_quakeservices13E0FA73(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::Route53::HostedZone", {"Name": "quake.services."}
        )

    def test_quake2servicesAEACB3A8(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::Route53::HostedZone", {"Name": "quake2.services."}
        )

    def test_quake3services35191D74(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::Route53::HostedZone", {"Name": "quake3.services."}
        )

