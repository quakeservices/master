from typing import Optional

from aws_cdk import Stack
from aws_cdk import aws_apigateway as apigateway
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as aws_lambda
from aws_cdk import aws_lambda_python_alpha as _lambda_python
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from constructs import Construct

from deployment.constants import APP_NAME, DOMAIN_NAME


class WebBackendStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.domain_name: str = DOMAIN_NAME
        self.sub_domain: str = "api" + DOMAIN_NAME
        self.zone = self._get_zone(DOMAIN_NAME)
        self.cert = self._create_certificate(self.domain_name, [self.sub_domain])
        self.table = self._get_table()

        self.handler = self._create_lambda_function()
        self.api = self._create_api_gateway()
        self._create_route53_entries()

    def _get_zone(self, zone: str) -> route53.IHostedZone:
        if not zone.endswith("."):
            zone += "."

        return route53.HostedZone.from_lookup(self, "zone", domain_name=zone)

    def _get_table(self) -> dynamodb.ITable:
        return dynamodb.Table.from_table_name(
            self,
            "table",
            table_name=APP_NAME,
        )

    def _create_certificate(
        self,
        domain_name: str,
        san: Optional[list[str]] = None,
        certificate_name: str = "certificate",
    ) -> acm.Certificate:
        return acm.Certificate(
            self,
            certificate_name,
            domain_name=domain_name,
            subject_alternative_names=san,
            validation=acm.CertificateValidation.from_dns(self.zone),
        )

    def _create_lambda_function(self, entry: str = "lib/web-backend"):
        """
        Define Lambda function
        """

        handler = _lambda_python.PythonFunction(
            self,
            "web-backend-handler",
            entry=entry,
            runtime=aws_lambda.Runtime.PYTHON_3_9,
        )

        self.table.grant_read_data(handler.role)

        return handler

    def _create_api_domain(self) -> apigateway.DomainNameOptions:
        return apigateway.DomainNameOptions(
            certificate=self.cert,
            domain_name=self.sub_domain,
            endpoint_type=apigateway.EndpointType.REGIONAL,
            security_policy=apigateway.SecurityPolicy.TLS_1_2,
        )

    def _create_api_gateway(self) -> apigateway.RestApi:
        return apigateway.LambdaRestApi(
            self,
            "api",
            handler=self.handler,
            rest_api_name=APP_NAME,
            domain_name=self._create_api_domain(),
            endpoint_types=[apigateway.EndpointType.REGIONAL],
            disable_execute_api_endpoint=True,
        )

    def _create_route53_entries(self):
        """
        Create Route53 entries
        """
        target = route53.RecordTarget.from_alias(route53_targets.ApiGateway(self.api))

        route53.ARecord(
            self, "api-v4", zone=self.zone, record_name="api", target=target
        )
        route53.AaaaRecord(
            self,
            "api-v6",
            zone=self.zone,
            record_name="api",
            target=target,
        )
