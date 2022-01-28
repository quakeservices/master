import os
from typing import Dict, List

from aws_cdk import (
    aws_apigateway as apigateway,
    aws_certificatemanager as certificatemanager,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_lambda_python as _lambda_python,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    core as cdk,
)


class WebBackendStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.region = "ap-southeast-2"
        self.domain_name = "quake.services"

        self.backend = self._create_lambda_function()
        self.api = self._create_api_gateway()
        self._create_route53_entries()

    def _create_dynamodb_access_policy(self, resources: List[str] = ["*"]):
        return iam.PolicyStatement(
            resources=resources,
            actions=[
                "dynamodb:Get*",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:Describe*",
                "dynamodb:List*",
            ],
        )

    def _create_lambda_function(self, entry: str = "lib/web-backend"):
        """
        Define Lambda function
        """

        backend = _lambda_python.PythonFunction(
            self,
            "web-backend-handler",
            entry=entry,
            runtime=_lambda.Runtime.PYTHON_3_9,
        )

        policy = self._create_dynamodb_access_policy()

        backend.add_to_role_policy(statement=policy)

        return backend

    def _define_cert_and_domain(
        self,
        certificate_id: str = "6744abde-0b71-4aa5-94b1-a9f554fb1116",
        record_name: str = "api",
    ) -> Dict:
        """
        Get existing wildcard certificate and
        Define domain name and certificate to use for API Gateway
        """
        arn = "arn:aws:acm:{region}:{account}:certificate/{cert}".format(
            region=self.region,
            account=os.getenv("CDK_DEFAULT_ACCOUNT"),
            cert=certificate_id,
        )

        certificate = certificatemanager.Certificate.from_certificate_arn(
            self, "wildcard_cert", arn
        )

        return {
            "domain_name": f"{record_name}.{self.domain_name}",
            "certificate": certificate,
        }

    def _create_api_gateway(self):
        """
        Define API Gateway
        """
        domain = self._define_cert_and_domain()

        return apigateway.LambdaRestApi(
            self,
            "api",
            domain_name=domain,
            handler=self.backend,
            default_cors_preflight_options={
                "allow_origins": [f"www.{self.domain_name}"],
                "allow_methods": ["GET"],
            },
        )

    def _create_route53_entries(self):
        """
        Create Route53 entries
        """
        zone = route53.HostedZone.from_lookup(
            self, "zone", domain_name=self.domain_name
        )

        route53.ARecord(
            self,
            "alias",
            zone=zone,
            record_name="api",
            target=route53.AddressRecordTarget.from_alias(
                route53_targets.ApiGateway(self.api)
            ),
        )
