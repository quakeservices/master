import pytest
from aws_cdk.assertions import Match, Template
from deployment.stacks import WebBackendStack


class TestQuakeservicesBackend:
    @pytest.fixture(scope="class")
    def stack_template(self, stack_app, stack_env_us_west_2):
        return Template.from_stack(
            WebBackendStack(stack_app, "test-backend", env=stack_env_us_west_2)
        )

    def test_certificateEC031123(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::CertificateManager::Certificate",
            {
                "DomainName": "quake.services",
                "DomainValidationOptions": [
                    {"DomainName": "quake.services", "HostedZoneId": "DUMMY"},
                    {"DomainName": "apiquake.services", "HostedZoneId": "DUMMY"},
                ],
                "SubjectAlternativeNames": ["apiquake.services"],
                "ValidationMethod": "DNS",
            },
        )

    def test_webbackendhandlerServiceRole6FB5ABE5(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::IAM::Role",
            {
                "AssumeRolePolicyDocument": {
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {"Service": "lambda.amazonaws.com"},
                        }
                    ],
                    "Version": "2012-10-17",
                },
                "ManagedPolicyArns": [
                    {
                        "Fn::Join": [
                            Match.any_value(),
                            [
                                "arn:",
                                {"Ref": "AWS::Partition"},
                                ":iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
                            ],
                        ]
                    }
                ],
            },
        )

    def test_webbackendhandlerServiceRoleDefaultPolicyA69BE70E(self, stack_template):
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
                                "dynamodb:DescribeTable",
                            ],
                            "Effect": "Allow",
                            "Resource": [
                                {
                                    "Fn::Join": [
                                        Match.any_value(),
                                        [
                                            "arn:",
                                            {"Ref": "AWS::Partition"},
                                            ":dynamodb:us-west-2:123456789012:table/quakeservices",
                                        ],
                                    ]
                                },
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

    def test_webbackendhandlerBCF48DA7(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::Lambda::Function",
            {
                "Code": {
                    "S3Bucket": Match.any_value(),
                    "S3Key": Match.any_value(),
                },
                "Role": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                "Handler": "index.handler",
                "Runtime": "python3.9",
            },
        )

    def test_apiC8550315(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ApiGateway::RestApi",
            {
                "DisableExecuteApiEndpoint": True,
                "EndpointConfiguration": {"Types": ["REGIONAL"]},
                "Name": Match.any_value(),
            },
        )

    def test_apiCloudWatchRoleAC81D93E(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::IAM::Role",
            {
                "AssumeRolePolicyDocument": {
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {"Service": "apigateway.amazonaws.com"},
                        }
                    ],
                    "Version": "2012-10-17",
                },
                "ManagedPolicyArns": [
                    {
                        "Fn::Join": [
                            Match.any_value(),
                            [
                                "arn:",
                                {"Ref": "AWS::Partition"},
                                ":iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs",
                            ],
                        ]
                    }
                ],
            },
        )

    def test_apiAccount57E28B43(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ApiGateway::Account",
            {"CloudWatchRoleArn": {"Fn::GetAtt": [Match.any_value(), "Arn"]}},
        )

    def test_apiDeployment149F1294c35b4cbf30c2149893a859f628a1bd1c(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::ApiGateway::Deployment",
            {
                "RestApiId": {"Ref": Match.any_value()},
                "Description": "Automatically created by the RestApi construct",
            },
        )

    def test_apiDeploymentStageprod896C8101(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ApiGateway::Stage",
            {
                "RestApiId": {"Ref": Match.any_value()},
                "DeploymentId": {"Ref": Match.any_value()},
                "StageName": Match.any_value(),
            },
        )

    def test_apiCustomDomain64773C4F(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ApiGateway::DomainName",
            {
                "DomainName": "apiquake.services",
                "EndpointConfiguration": {"Types": ["REGIONAL"]},
                "RegionalCertificateArn": {"Ref": Match.any_value()},
                "SecurityPolicy": "TLS_1_2",
            },
        )

    def test_apiCustomDomainMapquakeservicesbackendapiFB5EFE685DE1BEEE(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::ApiGateway::BasePathMapping",
            {
                "DomainName": {"Ref": Match.any_value()},
                "RestApiId": {"Ref": Match.any_value()},
                "Stage": {"Ref": Match.any_value()},
            },
        )

    def test_apiproxy4EA44110(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ApiGateway::Resource",
            {
                "ParentId": {"Fn::GetAtt": [Match.any_value(), "RootResourceId"]},
                "PathPart": "{proxy+}",
                "RestApiId": {"Ref": Match.any_value()},
            },
        )

    def test_apiproxyANYApiPermissionquakeservicesbackendapiFB5EFE68ANYproxyD547B541(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::Lambda::Permission",
            {
                "Action": "lambda:InvokeFunction",
                "FunctionName": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                "Principal": "apigateway.amazonaws.com",
                "SourceArn": {
                    "Fn::Join": [
                        Match.any_value(),
                        [
                            "arn:",
                            {"Ref": "AWS::Partition"},
                            ":execute-api:us-west-2:123456789012:",
                            {"Ref": Match.any_value()},
                            "/",
                            {"Ref": Match.any_value()},
                            "/*/*",
                        ],
                    ]
                },
            },
        )

    def test_apiproxyANYApiPermissionTestquakeservicesbackendapiFB5EFE68ANYproxy8F501B6E(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::Lambda::Permission",
            {
                "Action": "lambda:InvokeFunction",
                "FunctionName": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                "Principal": "apigateway.amazonaws.com",
                "SourceArn": {
                    "Fn::Join": [
                        Match.any_value(),
                        [
                            "arn:",
                            {"Ref": "AWS::Partition"},
                            ":execute-api:us-west-2:123456789012:",
                            {"Ref": Match.any_value()},
                            "/test-invoke-stage/*/*",
                        ],
                    ]
                },
            },
        )

    def test_apiproxyANY7F13F09C(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ApiGateway::Method",
            {
                "HttpMethod": Match.any_value(),
                "ResourceId": {"Ref": Match.any_value()},
                "RestApiId": {"Ref": Match.any_value()},
                "AuthorizationType": "NONE",
                "Integration": {
                    "IntegrationHttpMethod": "POST",
                    "Type": "AWS_PROXY",
                    "Uri": {
                        "Fn::Join": [
                            Match.any_value(),
                            [
                                "arn:",
                                {"Ref": "AWS::Partition"},
                                ":apigateway:us-west-2:lambda:path/2015-03-31/functions/",
                                {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                                "/invocations",
                            ],
                        ]
                    },
                },
            },
        )

    def test_apiANYApiPermissionquakeservicesbackendapiFB5EFE68ANYB8B5B8F4(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::Lambda::Permission",
            {
                "Action": "lambda:InvokeFunction",
                "FunctionName": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                "Principal": "apigateway.amazonaws.com",
                "SourceArn": {
                    "Fn::Join": [
                        Match.any_value(),
                        [
                            "arn:",
                            {"Ref": "AWS::Partition"},
                            ":execute-api:us-west-2:123456789012:",
                            {"Ref": Match.any_value()},
                            "/",
                            {"Ref": Match.any_value()},
                            "/*/",
                        ],
                    ]
                },
            },
        )

    def test_apiANYApiPermissionTestquakeservicesbackendapiFB5EFE68ANY16793868(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::Lambda::Permission",
            {
                "Action": "lambda:InvokeFunction",
                "FunctionName": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                "Principal": "apigateway.amazonaws.com",
                "SourceArn": {
                    "Fn::Join": [
                        Match.any_value(),
                        [
                            "arn:",
                            {"Ref": "AWS::Partition"},
                            ":execute-api:us-west-2:123456789012:",
                            {"Ref": Match.any_value()},
                            "/test-invoke-stage/*/",
                        ],
                    ]
                },
            },
        )

    def test_apiANYB3DF8C3C(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::ApiGateway::Method",
            {
                "HttpMethod": Match.any_value(),
                "ResourceId": {"Fn::GetAtt": [Match.any_value(), "RootResourceId"]},
                "RestApiId": {"Ref": Match.any_value()},
                "AuthorizationType": "NONE",
                "Integration": {
                    "IntegrationHttpMethod": "POST",
                    "Type": "AWS_PROXY",
                    "Uri": {
                        "Fn::Join": [
                            Match.any_value(),
                            [
                                "arn:",
                                {"Ref": "AWS::Partition"},
                                ":apigateway:us-west-2:lambda:path/2015-03-31/functions/",
                                {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                                "/invocations",
                            ],
                        ]
                    },
                },
            },
        )

    def test_apiv4465A3CCA(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::Route53::RecordSet",
            {
                "Name": "api.quake.services.",
                "Type": Match.any_value(),
                "AliasTarget": {
                    "DNSName": {
                        "Fn::GetAtt": [Match.any_value(), "RegionalDomainName"]
                    },
                    "HostedZoneId": {
                        "Fn::GetAtt": [Match.any_value(), "RegionalHostedZoneId"]
                    },
                },
                "HostedZoneId": "DUMMY",
            },
        )

    def test_apiv64BE76393(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::Route53::RecordSet",
            {
                "Name": "api.quake.services.",
                "Type": "AAAA",
                "AliasTarget": {
                    "DNSName": {
                        "Fn::GetAtt": [Match.any_value(), "RegionalDomainName"]
                    },
                    "HostedZoneId": {
                        "Fn::GetAtt": [Match.any_value(), "RegionalHostedZoneId"]
                    },
                },
                "HostedZoneId": "DUMMY",
            },
        )
