import pytest
from aws_cdk.assertions import Match, Template

from deployment.stacks.pipeline import PipelineStack


@pytest.mark.cdk
@pytest.mark.unit_test
@pytest.mark.skip(reason="Stack not complete")
class TestQuakeservicesPipeline:
    @pytest.fixture(scope="class")
    def stack_template(self, stack_app, stack_env_us_west_2):
        return Template.from_stack(
            PipelineStack(stack_app, "test-pipeline", env=stack_env_us_west_2)
        )

    def test_pipelinePipelineArtifactsBucketC2CD5B5E(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::S3::Bucket",
            {
                "BucketEncryption": {
                    "ServerSideEncryptionConfiguration": [
                        {"ServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms"}}
                    ]
                },
                "PublicAccessBlockConfiguration": {
                    "BlockPublicAcls": True,
                    "BlockPublicPolicy": True,
                    "IgnorePublicAcls": True,
                    "RestrictPublicBuckets": True,
                },
            },
        )

    def test_pipelinePipelineArtifactsBucketPolicy10A41055(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::S3::BucketPolicy",
            {
                "Bucket": {"Ref": Match.any_value()},
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": "s3:*",
                            "Condition": {"Bool": {"aws:SecureTransport": "false"}},
                            "Effect": "Deny",
                            "Principal": {"AWS": "*"},
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

    def test_pipelinePipelineRole7016E5DF(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::IAM::Role",
            {
                "AssumeRolePolicyDocument": {
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {"Service": "codepipeline.amazonaws.com"},
                        }
                    ],
                    "Version": "2012-10-17",
                }
            },
        )

    def test_pipelinePipelineRoleDefaultPolicy16010F3E(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::IAM::Policy",
            {
                "PolicyDocument": {
                    "Statement": [
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
                        {
                            "Action": "sts:AssumeRole",
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

    def test_pipelinePipeline4163A4B1(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::CodePipeline::Pipeline",
            {
                "RoleArn": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                "Stages": [
                    {
                        "Actions": [
                            {
                                "ActionTypeId": {
                                    "Category": Match.any_value(),
                                    "Owner": "ThirdParty",
                                    "Provider": "GitHub",
                                    "Version": Match.any_value(),
                                },
                                "Configuration": {
                                    "Owner": Match.any_value(),
                                    "Repo": Match.any_value(),
                                    "Branch": "main",
                                    "OAuthToken": "{{resolve:secretsmanager:github-token:SecretString:::}}",
                                    "PollForSourceChanges": False,
                                },
                                "Name": "quakeservices_master",
                                "OutputArtifacts": [
                                    {"Name": "quakeservices_master_Source"}
                                ],
                                "RunOrder": 1,
                            }
                        ],
                        "Name": Match.any_value(),
                    },
                    {
                        "Actions": [
                            {
                                "ActionTypeId": {
                                    "Category": Match.any_value(),
                                    "Owner": "AWS",
                                    "Provider": Match.any_value(),
                                    "Version": Match.any_value(),
                                },
                                "Configuration": {
                                    "ProjectName": {"Ref": Match.any_value()},
                                    "EnvironmentVariables": '[{"name":"_PROJECT_CONFIG_HASH","type":"PLAINTEXT","value":"f489e70cca2b73939aa924b6c6071e1ff830dcaca1076b4274a66e837cb326aa"}]',
                                },
                                "InputArtifacts": [
                                    {"Name": "quakeservices_master_Source"}
                                ],
                                "Name": Match.any_value(),
                                "OutputArtifacts": [{"Name": "Synth_Output"}],
                                "RoleArn": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                                "RunOrder": 1,
                            }
                        ],
                        "Name": Match.any_value(),
                    },
                    {
                        "Actions": [
                            {
                                "ActionTypeId": {
                                    "Category": Match.any_value(),
                                    "Owner": "AWS",
                                    "Provider": Match.any_value(),
                                    "Version": Match.any_value(),
                                },
                                "Configuration": {
                                    "ProjectName": {"Ref": Match.any_value()},
                                    "EnvironmentVariables": '[{"name":"_PROJECT_CONFIG_HASH","type":"PLAINTEXT","value":"7e06386ead240eaf79a9de368a93d7b622197fcce40d01b2096e17995e369df3"}]',
                                },
                                "InputArtifacts": [{"Name": "Synth_Output"}],
                                "Name": "SelfMutate",
                                "RoleArn": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                                "RunOrder": 1,
                            }
                        ],
                        "Name": Match.any_value(),
                    },
                ],
                "ArtifactStore": {"Location": {"Ref": Match.any_value()}, "Type": "S3"},
                "Name": Match.any_value(),
                "RestartExecutionOnUpdate": True,
            },
        )

    def test_pipelinePipelineSourcequakeservicesmasterWebhookResource5C7F22DF(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::CodePipeline::Webhook",
            {
                "Authentication": "GITHUB_HMAC",
                "AuthenticationConfiguration": {
                    "SecretToken": "{{resolve:secretsmanager:github-token:SecretString:::}}"
                },
                "Filters": [
                    {"JsonPath": "$.ref", "MatchEquals": "refs/heads/{Branch}"}
                ],
                "TargetAction": "quakeservices_master",
                "TargetPipeline": {"Ref": Match.any_value()},
                "TargetPipelineVersion": 1,
                "RegisterWithThirdParty": True,
            },
        )

    def test_pipelinePipelineBuildSynthCdkBuildProjectRole0C39D18F(
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
                            "Principal": {"Service": "codebuild.amazonaws.com"},
                        }
                    ],
                    "Version": "2012-10-17",
                }
            },
        )

    def test_pipelinePipelineBuildSynthCdkBuildProjectRoleDefaultPolicyB3981181(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::IAM::Policy",
            {
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": [
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            "Effect": "Allow",
                            "Resource": [
                                {
                                    "Fn::Join": [
                                        Match.any_value(),
                                        [
                                            "arn:",
                                            {"Ref": "AWS::Partition"},
                                            ":logs:us-west-2:123456789012:log-group:/aws/codebuild/",
                                            {"Ref": Match.any_value()},
                                        ],
                                    ]
                                },
                                {
                                    "Fn::Join": [
                                        Match.any_value(),
                                        [
                                            "arn:",
                                            {"Ref": "AWS::Partition"},
                                            ":logs:us-west-2:123456789012:log-group:/aws/codebuild/",
                                            {"Ref": Match.any_value()},
                                            ":*",
                                        ],
                                    ]
                                },
                            ],
                        },
                        {
                            "Action": [
                                "codebuild:CreateReportGroup",
                                "codebuild:CreateReport",
                                "codebuild:UpdateReport",
                                "codebuild:BatchPutTestCases",
                                "codebuild:BatchPutCodeCoverages",
                            ],
                            "Effect": "Allow",
                            "Resource": {
                                "Fn::Join": [
                                    Match.any_value(),
                                    [
                                        "arn:",
                                        {"Ref": "AWS::Partition"},
                                        ":codebuild:us-west-2:123456789012:report-group/",
                                        {"Ref": Match.any_value()},
                                        "-*",
                                    ],
                                ]
                            },
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

    def test_pipelinePipelineBuildSynthCdkBuildProject4237770A(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::CodeBuild::Project",
            {
                "Artifacts": {"Type": "CODEPIPELINE"},
                "Environment": {
                    "ComputeType": "BUILD_GENERAL1_SMALL",
                    "Image": "aws/codebuild/standard:5.0",
                    "ImagePullCredentialsType": "CODEBUILD",
                    "PrivilegedMode": False,
                    "Type": "LINUX_CONTAINER",
                },
                "ServiceRole": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                "Source": {
                    "BuildSpec": '{\n  "version": "0.2",\n  "phases": {\n    "build": {\n      "commands": [\n        "npm install -g aws-cdk",\n        "python -m pip install -r deployment/requirements.txt",\n        "cdk synth"\n      ]\n    }\n  },\n  "artifacts": {\n    "base-directory": "cdk.out",\n    "files": "**/*"\n  }\n}',
                    "Type": "CODEPIPELINE",
                },
                "Cache": {"Type": "NO_CACHE"},
                "Description": "Pipeline step test-pipeline/Pipeline/Build/Synth",
                "EncryptionKey": "alias/aws/s3",
            },
        )

    def test_pipelineCodeBuildActionRole4D1FDB53(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::IAM::Role",
            {
                "AssumeRolePolicyDocument": {
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Condition": {
                                "Bool": {
                                    "aws:ViaAWSService": "codepipeline.amazonaws.com"
                                }
                            },
                            "Effect": "Allow",
                            "Principal": {
                                "AWS": {
                                    "Fn::Join": [
                                        Match.any_value(),
                                        [
                                            "arn:",
                                            {"Ref": "AWS::Partition"},
                                            ":iam::123456789012:root",
                                        ],
                                    ]
                                }
                            },
                        }
                    ],
                    "Version": "2012-10-17",
                }
            },
        )

    def test_pipelineCodeBuildActionRoleDefaultPolicyE3C51929(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::IAM::Policy",
            {
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": [
                                "codebuild:BatchGetBuilds",
                                "codebuild:StartBuild",
                                "codebuild:StopBuild",
                            ],
                            "Effect": "Allow",
                            "Resource": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                        },
                        {
                            "Action": [
                                "codebuild:BatchGetBuilds",
                                "codebuild:StartBuild",
                                "codebuild:StopBuild",
                            ],
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

    def test_pipelineUpdatePipelineSelfMutationRole91820177(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::IAM::Role",
            {
                "AssumeRolePolicyDocument": {
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {"Service": "codebuild.amazonaws.com"},
                        }
                    ],
                    "Version": "2012-10-17",
                }
            },
        )

    def test_pipelineUpdatePipelineSelfMutationRoleDefaultPolicy095404B8(
        self, stack_template
    ):
        stack_template.has_resource_properties(
            "AWS::IAM::Policy",
            {
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": [
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            "Effect": "Allow",
                            "Resource": [
                                {
                                    "Fn::Join": [
                                        Match.any_value(),
                                        [
                                            "arn:",
                                            {"Ref": "AWS::Partition"},
                                            ":logs:us-west-2:123456789012:log-group:/aws/codebuild/",
                                            {"Ref": Match.any_value()},
                                        ],
                                    ]
                                },
                                {
                                    "Fn::Join": [
                                        Match.any_value(),
                                        [
                                            "arn:",
                                            {"Ref": "AWS::Partition"},
                                            ":logs:us-west-2:123456789012:log-group:/aws/codebuild/",
                                            {"Ref": Match.any_value()},
                                            ":*",
                                        ],
                                    ]
                                },
                            ],
                        },
                        {
                            "Action": [
                                "codebuild:CreateReportGroup",
                                "codebuild:CreateReport",
                                "codebuild:UpdateReport",
                                "codebuild:BatchPutTestCases",
                                "codebuild:BatchPutCodeCoverages",
                            ],
                            "Effect": "Allow",
                            "Resource": {
                                "Fn::Join": [
                                    Match.any_value(),
                                    [
                                        "arn:",
                                        {"Ref": "AWS::Partition"},
                                        ":codebuild:us-west-2:123456789012:report-group/",
                                        {"Ref": Match.any_value()},
                                        "-*",
                                    ],
                                ]
                            },
                        },
                        {
                            "Action": "sts:AssumeRole",
                            "Condition": {
                                "ForAnyValue:StringEquals": {
                                    "iam:ResourceTag/aws-cdk:bootstrap-role": [
                                        "image-publishing",
                                        "file-publishing",
                                        "deploy",
                                    ]
                                }
                            },
                            "Effect": "Allow",
                            "Resource": "arn:*:iam::123456789012:role/*",
                        },
                        {
                            "Action": "cloudformation:DescribeStacks",
                            "Effect": "Allow",
                            "Resource": "*",
                        },
                        {"Action": "s3:ListBucket", "Effect": "Allow", "Resource": "*"},
                        {
                            "Action": ["s3:GetObject*", "s3:GetBucket*", "s3:List*"],
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

    def test_pipelineUpdatePipelineSelfMutation14A96D2F(self, stack_template):
        stack_template.has_resource_properties(
            "AWS::CodeBuild::Project",
            {
                "Artifacts": {"Type": "CODEPIPELINE"},
                "Environment": {
                    "ComputeType": "BUILD_GENERAL1_SMALL",
                    "Image": "aws/codebuild/standard:5.0",
                    "ImagePullCredentialsType": "CODEBUILD",
                    "PrivilegedMode": False,
                    "Type": "LINUX_CONTAINER",
                },
                "ServiceRole": {"Fn::GetAtt": [Match.any_value(), "Arn"]},
                "Source": {
                    "BuildSpec": '{\n  "version": "0.2",\n  "phases": {\n    "install": {\n      "commands": [\n        "npm install -g aws-cdk@2"\n      ]\n    },\n    "build": {\n      "commands": [\n        "cdk -a . deploy test-pipeline --require-approval=never --verbose"\n      ]\n    }\n  }\n}',
                    "Type": "CODEPIPELINE",
                },
                "Cache": {"Type": "NO_CACHE"},
                "Description": "Pipeline step test-pipeline/Pipeline/UpdatePipeline/SelfMutate",
                "EncryptionKey": "alias/aws/s3",
                "Name": "test-selfupdate",
            },
        )
