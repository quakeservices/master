import pytest
from aws_cdk.assertions import Match, Template
from deployment.stacks import WebFrontendStack


class TestQuakeservicesFrontend:
    @pytest.fixture(scope="class")
    def stack_template(self, stack_app, stack_env_us_east_1):
        return Template.from_stack(
            WebFrontendStack(stack_app, "test-frontend", env=stack_env_us_east_1)
        )

    def test_certificateEC031123(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::CertificateManager::Certificate",
            {
                "DomainName": "quake.services",
                "DomainValidationOptions": [
                    {"DomainName": "quake.services", "HostedZoneId": "DUMMY"},
                    {"DomainName": "wwwquake.services", "HostedZoneId": "DUMMY"},
                ],
                "SubjectAlternativeNames": ["wwwquake.services"],
                "ValidationMethod": "DNS",
            },
        )

    def test_assetbucket82C8F93D(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::S3::Bucket",
            {
                "Tags": [
                    {"Key": "aws-cdk:auto-delete-objects", "Value": "true"},
                    {"Key": Match.any_value(), "Value": "true"},
                ]
            },
        )

    def test_assetbucketPolicyD9EA0653(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::S3::BucketPolicy",
            {
                "Bucket": {"Ref": Match.any_value()},
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": ["s3:GetBucket*", "s3:List*", "s3:DeleteObject*"],
                            "Effect": "Allow",
                            "Principal": {
                                "AWS": {"Fn::GetAtt": [Match.any_value(), "Arn"]}
                            },
                            "Resource": [
                                {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                                {
                                    "Fn::Join": [
                                        Match.any_value(),
                                        [
                                            {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                                            "/*",
                                        ],
                                    ]
                                },
                            ],
                        },
                        {
                            "Action": "s3:GetObject",
                            "Effect": "Allow",
                            "Principal": {
                                "CanonicalUser": {
                                    "Fn::GetAtt": [
                                        Match.any_value(),
                                        "S3CanonicalUserId",
                                    ]
                                }
                            },
                            "Resource": {
                                "Fn::Join": [
                                    Match.any_value(),
                                    [{"Fn::GetAtt": [Match.any_value(), "Arn"]}, "/*"],
                                ]
                            },
                        },
                    ],
                    "Version": "2012-10-17",
                },
            },
        )

    def test_assetbucketAutoDeleteObjectsCustomResourceBABF36A1(self, stack_template):
        stack_template.has_resource_properties(
            "Custom::S3AutoDeleteObjects",
            {
                "ServiceToken": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                "BucketName": {"Ref": Match.any_value()},
            },
        )

    def test_CustomS3AutoDeleteObjectsCustomResourceProviderRole3B1BD092(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::IAM::Role",
            {
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {"Service": "lambda.amazonaws.com"},
                        }
                    ],
                },
                "ManagedPolicyArns": [
                    {
                        "Fn::Sub": "arn:${AWS::Partition}:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
                    }
                ],
            },
        )

    def test_CustomS3AutoDeleteObjectsCustomResourceProviderHandler9D90184F(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::Lambda::Function",
            {
                "Code": {
                    "S3Bucket": Match.any_value(),
                    "S3Key": Match.any_value(),
                },
                "Timeout": 900,
                "MemorySize": 128,
                "Handler": "__entrypoint__.handler",
                "Role": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                "Runtime": "nodejs12.x",
                "Description": {
                    "Fn::Join": [
                        Match.any_value(),
                        [
                            "Lambda function for auto-deleting objects in ",
                            {"Ref": Match.any_value()},
                            " S3 bucket.",
                        ],
                    ]
                },
            },
        )

    def test_redirectbucketF8411844(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::S3::Bucket",
            {
                "Tags": [{"Key": "aws-cdk:auto-delete-objects", "Value": "true"}],
                "WebsiteConfiguration": {
                    "RedirectAllRequestsTo": {
                        "HostName": "wwwquake.services",
                        "Protocol": "https",
                    }
                },
            },
        )

    def test_redirectbucketPolicy326DB78E(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::S3::BucketPolicy",
            {
                "Bucket": {"Ref": Match.any_value()},
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": ["s3:GetBucket*", "s3:List*", "s3:DeleteObject*"],
                            "Effect": "Allow",
                            "Principal": {
                                "AWS": {"Fn::GetAtt": [Match.any_value(), "Arn"]}
                            },
                            "Resource": [
                                {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                                {
                                    "Fn::Join": [
                                        Match.any_value(),
                                        [
                                            {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                                            "/*",
                                        ],
                                    ]
                                },
                            ],
                        }
                    ],
                    "Version": "2012-10-17",
                },
            },
        )

    def test_redirectbucketAutoDeleteObjectsCustomResource35F95C2D(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "Custom::S3AutoDeleteObjects",
            {
                "ServiceToken": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                "BucketName": {"Ref": Match.any_value()},
            },
        )

    def test_sitedistributionOrigin1S3Origin39961CD6(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::CloudFront::CloudFrontOriginAccessIdentity",
            {"CloudFrontOriginAccessIdentityConfig": {"Comment": Match.any_value()}},
        )

    def test_sitedistribution22589041(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::CloudFront::Distribution",
            {
                "DistributionConfig": {
                    "Aliases": ["wwwquake.services"],
                    "DefaultCacheBehavior": {
                        "CachePolicyId": Match.any_value(),
                        "Compress": True,
                        "TargetOriginId": Match.any_value(),
                        "ViewerProtocolPolicy": "redirect-to-https",
                    },
                    "Enabled": True,
                    "HttpVersion": "http2",
                    "IPV6Enabled": True,
                    "Origins": [
                        {
                            "DomainName": {
                                "Fn::GetAtt": [Match.any_value(), "RegionalDomainName"]
                            },
                            "Id": Match.any_value(),
                            "S3OriginConfig": {
                                "OriginAccessIdentity": {
                                    "Fn::Join": [
                                        Match.any_value(),
                                        [
                                            "origin-access-identity/cloudfront/",
                                            {"Ref": Match.any_value()},
                                        ],
                                    ]
                                }
                            },
                        }
                    ],
                    "ViewerCertificate": {
                        "AcmCertificateArn": {"Ref": Match.any_value()},
                        "MinimumProtocolVersion": "TLSv1.2_2021",
                        "SslSupportMethod": "sni-only",
                    },
                }
            },
        )

    def test_redirectdistribution6C7C9A9C(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::CloudFront::Distribution",
            {
                "DistributionConfig": {
                    "Aliases": ["quake.services"],
                    "DefaultCacheBehavior": {
                        "CachePolicyId": Match.any_value(),
                        "Compress": True,
                        "TargetOriginId": Match.any_value(),
                        "ViewerProtocolPolicy": "redirect-to-https",
                    },
                    "Enabled": True,
                    "HttpVersion": "http2",
                    "IPV6Enabled": True,
                    "Origins": [
                        {
                            "CustomOriginConfig": {
                                "OriginProtocolPolicy": "http-only",
                                "OriginSSLProtocols": ["TLSv1.2"],
                            },
                            "DomainName": {
                                "Fn::Select": [
                                    2,
                                    {
                                        "Fn::Split": [
                                            "/",
                                            {
                                                "Fn::GetAtt": [
                                                    Match.any_value(),
                                                    "WebsiteURL",
                                                ]
                                            },
                                        ]
                                    },
                                ]
                            },
                            "Id": Match.any_value(),
                        }
                    ],
                    "ViewerCertificate": {
                        "AcmCertificateArn": {"Ref": Match.any_value()},
                        "MinimumProtocolVersion": "TLSv1.2_2021",
                        "SslSupportMethod": "sni-only",
                    },
                }
            },
        )

    def test_assetdeploymentAwsCliLayer2C55C187(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::Lambda::LayerVersion",
            {
                "Content": {
                    "S3Bucket": Match.any_value(),
                    "S3Key": Match.any_value(),
                },
                "Description": "/opt/awscli/aws",
            },
        )

    def test_assetdeploymentCustomResourceC5B29AD2(self, stack_template):
        stack_template.has_resource_properties(
            "Custom::CDKBucketDeployment",
            {
                "ServiceToken": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                "SourceBucketNames": [Match.any_value()],
                "SourceObjectKeys": [Match.any_value()],
                "DestinationBucketName": {"Ref": Match.any_value()},
                "Prune": True,
            },
        )

    def test_CustomCDKBucketDeployment8693BB64968944B69AAFB0CC9EB8756CServiceRole89A01265(
        self, stack_template
    ):
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

    def test_CustomCDKBucketDeployment8693BB64968944B69AAFB0CC9EB8756CServiceRoleDefaultPolicy88902FDF(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::IAM::Policy",
            {
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": ["s3:GetObject*", "s3:GetBucket*", "s3:List*"],
                            "Effect": "Allow",
                            "Resource": [
                                {
                                    "Fn::Join": [
                                        Match.any_value(),
                                        [
                                            "arn:",
                                            {"Ref": "AWS::Partition"},
                                            ":s3:::cdk-hnb659fds-assets-123456789012-us-east-1",
                                        ],
                                    ]
                                },
                                {
                                    "Fn::Join": [
                                        Match.any_value(),
                                        [
                                            "arn:",
                                            {"Ref": "AWS::Partition"},
                                            ":s3:::cdk-hnb659fds-assets-123456789012-us-east-1/*",
                                        ],
                                    ]
                                },
                            ],
                        },
                        {
                            "Action": [
                                "s3:GetObject*",
                                "s3:GetBucket*",
                                "s3:List*",
                                "s3:DeleteObject*",
                                "s3:PutObject",
                                "s3:PutObjectLegalHold",
                                "s3:PutObjectRetention",
                                "s3:PutObjectTagging",
                                "s3:PutObjectVersionTagging",
                                "s3:Abort*",
                            ],
                            "Effect": "Allow",
                            "Resource": [
                                {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                                {
                                    "Fn::Join": [
                                        Match.any_value(),
                                        [
                                            {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                                            "/*",
                                        ],
                                    ]
                                },
                            ],
                        },
                    ],
                    "Version": "2012-10-17",
                },
                "PolicyName": Match.any_value(),
                "Roles": [{"Ref": Match.any_value()}],
            },
        )

    def test_CustomCDKBucketDeployment8693BB64968944B69AAFB0CC9EB8756C81C01536(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::Lambda::Function",
            {
                "Code": {
                    "S3Bucket": Match.any_value(),
                    "S3Key": Match.any_value(),
                },
                "Role": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                "Handler": "index.handler",
                "Layers": [{"Ref": Match.any_value()}],
                "Runtime": "python3.7",
                "Timeout": 900,
            },
        )

    def test_route53sitev47447B695(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::Route53::RecordSet",
            {
                "Name": "quake.services.",
                "Type": Match.any_value(),
                "AliasTarget": {
                    "DNSName": {"Fn::GetAtt": [Match.any_value(), "DomainName"]},
                    "HostedZoneId": {
                        "Fn::FindInMap": [
                            "AWSCloudFrontPartitionHostedZoneIdMap",
                            {"Ref": "AWS::Partition"},
                            "zoneId",
                        ]
                    },
                },
                "HostedZoneId": "DUMMY",
            },
        )

    def test_route53sitev649621800(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::Route53::RecordSet",
            {
                "Name": "quake.services.",
                "Type": "AAAA",
                "AliasTarget": {
                    "DNSName": {"Fn::GetAtt": [Match.any_value(), "DomainName"]},
                    "HostedZoneId": {
                        "Fn::FindInMap": [
                            "AWSCloudFrontPartitionHostedZoneIdMap",
                            {"Ref": "AWS::Partition"},
                            "zoneId",
                        ]
                    },
                },
                "HostedZoneId": "DUMMY",
            },
        )

    def test_route53apexv49AFADB56(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::Route53::RecordSet",
            {
                "Name": "wwwquake.services.quake.services.",
                "Type": Match.any_value(),
                "AliasTarget": {
                    "DNSName": {"Fn::GetAtt": [Match.any_value(), "DomainName"]},
                    "HostedZoneId": {
                        "Fn::FindInMap": [
                            "AWSCloudFrontPartitionHostedZoneIdMap",
                            {"Ref": "AWS::Partition"},
                            "zoneId",
                        ]
                    },
                },
                "HostedZoneId": "DUMMY",
            },
        )

    def test_route53apexv6FD170A24(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::Route53::RecordSet",
            {
                "Name": "wwwquake.services.quake.services.",
                "Type": "AAAA",
                "AliasTarget": {
                    "DNSName": {"Fn::GetAtt": [Match.any_value(), "DomainName"]},
                    "HostedZoneId": {
                        "Fn::FindInMap": [
                            "AWSCloudFrontPartitionHostedZoneIdMap",
                            {"Ref": "AWS::Partition"},
                            "zoneId",
                        ]
                    },
                },
                "HostedZoneId": "DUMMY",
            },
        )
