import pytest
from aws_cdk.assertions import Match, Template

from deployment.stacks import MasterStack


class TestQuakeservicesMaster:
    @pytest.fixture(scope="class")
    def stack_template(self, stack_app, stack_env_us_west_2):
        return Template.from_stack(
            MasterStack(
                stack_app,
                "test-master",
                env=stack_env_us_west_2,
            )
        )

    def test_table8235A42E(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::DynamoDB::Table",
            {
                "KeySchema": [{"AttributeName": "address", "KeyType": "HASH"}],
                "AttributeDefinitions": [
                    {"AttributeName": "address", "AttributeType": Match.any_value()}
                ],
                "BillingMode": "PAY_PER_REQUEST",
                "TableName": Match.any_value(),
            },
        )

    def test_taskTaskRole99C98141(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::IAM::Role",
            {
                "AssumeRolePolicyDocument": {
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                        }
                    ],
                    "Version": "2012-10-17",
                }
            },
        )

    def test_taskTaskRoleDefaultPolicy08F0FEF8(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::IAM::Policy",
            {
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": [
                                "dynamodb:BatchGetItem",
                                "dynamodb:GetRecords",
                                "dynamodb:GetShardIterator",
                                "dynamodb:Query",
                                "dynamodb:GetItem",
                                "dynamodb:Scan",
                                "dynamodb:ConditionCheckItem",
                                "dynamodb:BatchWriteItem",
                                "dynamodb:PutItem",
                                "dynamodb:UpdateItem",
                                "dynamodb:DeleteItem",
                                "dynamodb:DescribeTable",
                            ],
                            "Effect": "Allow",
                            "Resource": [
                                {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                                {"Ref": "AWS::NoValue"},
                            ],
                        }
                    ],
                    "Version": "2012-10-17",
                },
                "PolicyName": Match.any_value(),
                "Roles": [{"Ref": Match.any_value()}],
            },
        )

    def test_task117DF50A(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ECS::TaskDefinition",
            {
                "ContainerDefinitions": [
                    {
                        "Essential": True,
                        "HealthCheck": {
                            "Command": ["CMD", "curl", "-f", "http://localhost:8080"],
                            "Interval": 30,
                            "Retries": 3,
                            "Timeout": 5,
                        },
                        "Image": "ghcr.io/quakeservices/master:latest",
                        "LogConfiguration": {
                            "LogDriver": "awslogs",
                            "Options": {
                                "awslogs-group": {"Ref": Match.any_value()},
                                "awslogs-stream-prefix": Match.any_value(),
                                "awslogs-region": "us-west-2",
                            },
                        },
                        "MemoryReservation": 1024,
                        "Name": Match.any_value(),
                        "PortMappings": [
                            {"ContainerPort": 27900, "Protocol": Match.any_value()},
                            {"ContainerPort": 8080, "Protocol": "tcp"},
                        ],
                        "StartTimeout": 15,
                        "StopTimeout": 15,
                        "RepositoryCredentials": {
                            "CredentialsParameter": {
                                "Fn::Join": [
                                    "",
                                    [
                                        "arn:",
                                        {"Ref": "AWS::Partition"},
                                        ":secretsmanager:us-west-2:123456789012:secret:quakeservices/github",
                                    ],
                                ]
                            }
                        },
                    }
                ],
                "Cpu": "512",
                "ExecutionRoleArn": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                "Family": Match.any_value(),
                "Memory": "1024",
                "NetworkMode": "awsvpc",
                "RequiresCompatibilities": ["FARGATE"],
                "TaskRoleArn": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
            },
        )

    def test_taskmasterLogGroup6386A43E(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::Logs::LogGroup", {"RetentionInDays": 14}
        )

    def test_taskExecutionRoleBA215F69(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::IAM::Role",
            {
                "AssumeRolePolicyDocument": {
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                        }
                    ],
                    "Version": "2012-10-17",
                }
            },
        )

    @pytest.mark.skip(reason="Too lazy to refactor tests just yet")
    def test_taskExecutionRoleDefaultPolicy25B52F7A(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::IAM::Policy",
            {
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": [
                                "ecr:BatchCheckLayerAvailability",
                                "ecr:GetDownloadUrlForLayer",
                                "ecr:BatchGetImage",
                            ],
                            "Effect": "Allow",
                            "Resource": {
                                "Fn::Join": [
                                    Match.any_value(),
                                    [
                                        "arn:",
                                        {"Ref": "AWS::Partition"},
                                        ":ecr:us-west-2:123456789012:repository/cdk-hnb659fds-container-assets-123456789012-us-west-2",
                                    ],
                                ]
                            },
                        },
                        {
                            "Action": "ecr:GetAuthorizationToken",
                            "Effect": "Allow",
                            "Resource": "*",
                        },
                        {
                            "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
                            "Effect": "Allow",
                            "Resource": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                        },
                    ],
                    "Version": "2012-10-17",
                },
                "PolicyName": Match.any_value(),
                "Roles": [{"Ref": Match.any_value()}],
            },
        )

    def test_nlbC39469D4(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ElasticLoadBalancingV2::LoadBalancer",
            {
                "LoadBalancerAttributes": [
                    {"Key": "deletion_protection.enabled", "Value": "false"},
                    {"Key": "load_balancing.cross_zone.enabled", "Value": "true"},
                ],
                "Name": Match.any_value(),
                "Scheme": "internet-facing",
                "Subnets": ["s-12345", "s-67890"],
                "Type": "network",
            },
        )

    def test_nlbudplistenerB76A4C27(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ElasticLoadBalancingV2::Listener",
            {
                "DefaultActions": [
                    {"TargetGroupArn": {"Ref": Match.any_value()}, "Type": "forward"}
                ],
                "LoadBalancerArn": {"Ref": Match.any_value()},
                "Port": 27900,
                "Protocol": "UDP",
            },
        )

    def test_nlbudplistenerquakeservicesGroup7C487B7C(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ElasticLoadBalancingV2::TargetGroup",
            {
                "HealthCheckPort": "8080",
                "HealthCheckProtocol": "HTTP",
                "Port": 27900,
                "Protocol": "UDP",
                "TargetGroupAttributes": [
                    {"Key": "preserve_client_ip.enabled", "Value": "true"}
                ],
                "TargetType": "ip",
                "VpcId": "vpc-12345",
            },
        )

    def test_serviceService7DDC3B7C(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ECS::Service",
            {
                "Cluster": Match.any_value(),
                "DeploymentConfiguration": {
                    "MaximumPercent": 200,
                    "MinimumHealthyPercent": 50,
                },
                "EnableECSManagedTags": False,
                "HealthCheckGracePeriodSeconds": 60,
                "LaunchType": "FARGATE",
                "LoadBalancers": [
                    {
                        "ContainerName": Match.any_value(),
                        "ContainerPort": 27900,
                        "TargetGroupArn": {"Ref": Match.any_value()},
                    }
                ],
                "NetworkConfiguration": {
                    "AwsvpcConfiguration": {
                        "AssignPublicIp": "ENABLED",
                        "SecurityGroups": [
                            {"Fn::GetAtt": [Match.any_value(), "GroupId"]}
                        ],
                        "Subnets": ["s-12345", "s-67890"],
                    }
                },
                "ServiceName": Match.any_value(),
                "TaskDefinition": {"Ref": Match.any_value()},
            },
        )

    @pytest.mark.skip(reason="Too lazy to refactor tests just yet")
    def test_serviceSecurityGroupF051F0EB(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::EC2::SecurityGroup",
            {
                "GroupDescription": "test-master/service/SecurityGroup",
                "SecurityGroupEgress": [
                    {
                        "CidrIp": "0.0.0.0/0",
                        "Description": "Allow all outbound traffic by default",
                        "IpProtocol": "-1",
                    }
                ],
                "VpcId": "vpc-12345",
            },
        )

    def test_alias68BF17F5(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::Route53::RecordSet",
            {
                "Name": "master.quake.services.",
                "Type": Match.any_value(),
                "AliasTarget": {
                    "DNSName": {
                        "Fn::Join": [
                            Match.any_value(),
                            [
                                "dualstack.",
                                {"Fn::GetAtt": [Match.any_value(), "DNSName"]},
                            ],
                        ]
                    },
                    "HostedZoneId": {
                        "Fn::GetAtt": [Match.any_value(), "CanonicalHostedZoneID"]
                    },
                },
                "HostedZoneId": "DUMMY",
            },
        )
