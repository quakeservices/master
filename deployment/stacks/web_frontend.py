import os
from typing import Optional

from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3deploy
from constructs import Construct

from deployment.constants import DOMAIN_NAME


class WebFrontendStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.domain: str = DOMAIN_NAME
        self.subdomain: str = "www" + DOMAIN_NAME
        self.zone = self._get_zone(DOMAIN_NAME)
        self.cert = self._create_certificate(self.domain, [self.subdomain])
        self._create_buckets()
        self._create_distributions()
        self._create_deployment()

        self._create_records()

    def _create_buckets(self) -> None:
        self.asset_bucket = self._create_asset_bucket()
        self.redirect_bucket = self._create_redirect_bucket()

    def _create_distributions(self) -> None:
        self.site_distribution = self._create_site_distribution()
        self.redirect_distribution = self._create_redirect_distribution()

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

    def _get_zone(self, zone: str) -> route53.IHostedZone:
        if not zone.endswith("."):
            zone += "."

        return route53.HostedZone.from_lookup(self, "zone", domain_name=zone)

    def _create_asset_bucket(self) -> s3.Bucket:
        """
        Create S3 Bucket for assets"
        """
        return s3.Bucket(
            self,
            "asset_bucket",
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

    def _create_redirect_bucket(self) -> s3.Bucket:
        return s3.Bucket(
            self,
            "redirect_bucket",
            website_redirect=s3.RedirectTarget(
                host_name=self.subdomain,
                protocol=s3.RedirectProtocol.HTTPS,
            ),
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

    def _create_deployment(self) -> s3deploy.BucketDeployment:
        assets_directory = "lib/web-frontend/dist"

        return s3deploy.BucketDeployment(
            self,
            "asset_deployment",
            sources=[s3deploy.Source.asset(assets_directory)],
            destination_bucket=self.asset_bucket,
        )

    def _create_site_distribution(self) -> cloudfront.Distribution:
        """
        Pull it all together in a CloudFront distribution
        """
        return cloudfront.Distribution(
            self,
            "site_distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(self.asset_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            domain_names=[self.subdomain],
            certificate=self.cert,
        )

    def _create_redirect_distribution(self) -> cloudfront.Distribution:
        return cloudfront.Distribution(
            self,
            "redirect_distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(self.redirect_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            domain_names=[self.domain],
            certificate=self.cert,
        )

    def _create_records(self) -> None:
        """
        Setup route53 entries
          A Record: subdomain.example.com
          A Record: example.com
          AAAA Record: example.com
          AAAA Record: subdomain.example.com
        """
        site_target = route53.RecordTarget.from_alias(
            route53_targets.CloudFrontTarget(self.site_distribution)
        )
        apex_target = route53.RecordTarget.from_alias(
            route53_targets.CloudFrontTarget(self.redirect_distribution)
        )

        self._create_route53_records(site_target, self.domain, "route53-site-")
        self._create_route53_records(apex_target, self.subdomain, "route53-apex-")

    def _create_route53_records(
        self, target, record_name: str, resource_name: str
    ) -> None:
        route53.ARecord(
            self,
            resource_name + "v4",
            zone=self.zone,
            record_name=record_name,
            target=target,
        )

        route53.AaaaRecord(
            self,
            resource_name + "v6",
            zone=self.zone,
            record_name=record_name,
            target=target,
        )
