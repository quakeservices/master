import os

import boto3
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_certificatemanager as certificatemanager
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from aws_cdk import aws_s3 as s3
from aws_cdk import core as cdk


class WebBackendDeployStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.zone = route53.HostedZone.from_lookup(
            self, "quake_services", domain_name="quake.services"
        )

        """
        Get existing certificate
        """
        arn = "arn:aws:acm:{region}:{account}:certificate/{cert}".format(
            region="us-west-2",
            account=os.getenv("CDK_DEFAULT_ACCOUNT"),
            cert="6744abde-0b71-4aa5-94b1-a9f554fb1116",
        )
        certificate = certificatemanager.Certificate.from_certificate_arn(
            self, "wildcard_cert", arn
        )

        policy = iam.PolicyStatement(
            resources=["*"],
            actions=[
                "dynamodb:Get*",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:Describe*",
                "dynamodb:List*",
            ],
        )

        """
        Define domain name and certificate to use for API Gateway
        """
        domain = {"domain_name": "api.quake.services", "certificate": certificate}

        """
        Get latest version of code
        There is probably a more elegant way of doing this
        But for now this works
        """
        s3_bucket_name = "web-backend-lambda-package"
        s3client = boto3.client("s3")
        latest_version = s3client.get_object_tagging(
            Bucket=s3_bucket_name, Key="function.zip"
        )
        bucket = s3.Bucket.from_bucket_name(self, "bucket", bucket_name=s3_bucket_name)

        """
        Define Lambda function
        """
        code = _lambda.Code.from_bucket(
            bucket=bucket,
            key="function.zip",
            object_version=latest_version.get("VersionId"),
        )

        backend = _lambda.Function(
            self,
            "web-backend",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda.lambda_handler",
            code=code,
        )

        backend.add_to_role_policy(statement=policy)

        """
        Define API Gateway
        """
        api = apigateway.LambdaRestApi(
            self,
            "QuakeServicesAPI",
            domain_name=domain,
            handler=backend,
            default_cors_preflight_options={
                "allow_origins": ["www.quake.services"],
                "allow_methods": ["GET"],
            },
        )
        """
        Create Route53 entries
        """
        route53.ARecord(
            self,
            "Alias",
            zone=self.zone,
            record_name="api",
            target=route53.AddressRecordTarget.from_alias(
                route53_targets.ApiGateway(api)
            ),
        )
