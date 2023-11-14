from typing import Any

from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elb
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from constructs import Construct

from deployment.constants import (
    APP_NAME,
    DEPLOYMENT_ENVIRONMENT,
    DOMAIN_NAME,
    MASTER_CPU,
    MASTER_HEALTHCHECK_PORT,
    MASTER_MEMORY,
    MASTER_PORT,
)
from deployment.models.fargate.task import (
    EcsHealthCheck,
    FargateTaskConfiguration,
    PortConfiguration,
    RegistryConfiguration,
)
from deployment.models.network.security_group import (
    SecurityGroupConfig,
    SecurityGroupRule,
)
from deployment.parts.dns.record import Record
from deployment.parts.fargate.task import FargateTask
from deployment.parts.network.security_group import SecurityGroup


class MasterStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = self._get_vpc()
        self.cluster = self._get_cluster()

        self.table = self._create_table()
        task_configuration = FargateTaskConfiguration(
            name="master",
            ports=self._ports(),
            healthcheck=self._healthcheck(),
            deployment_environment=DEPLOYMENT_ENVIRONMENT,
            registry=RegistryConfiguration(
                name="ghcr",
                namespace="quakeservices",
                image="master",
                tag="latest",
            ),
            cpu=MASTER_CPU,
            memory=MASTER_MEMORY,
        )
        self.task = FargateTask(
            self,
            "task",
            config=task_configuration,
        )
        self._grant_table_read_write_to_task()
        self.nlb = self._create_network_load_balancer()
        self._create_service_and_nlb()
        self._create_a_record()

    def _ports(self) -> list[PortConfiguration]:
        return [PortConfiguration(port=MASTER_PORT, protocol="UDP")]

    def _healthcheck(self) -> EcsHealthCheck:
        return EcsHealthCheck(
            port=MASTER_HEALTHCHECK_PORT, protocol="TCP", scheme="http"
        )

    def _get_vpc(self) -> ec2.IVpc:
        return ec2.Vpc.from_lookup(self, "vpc", vpc_name=APP_NAME)

    def _get_zone(self) -> route53.IHostedZone:
        return route53.HostedZone.from_lookup(self, "domain", domain_name=DOMAIN_NAME)

    def _get_cluster(self) -> ecs.ICluster:
        return ecs.Cluster.from_cluster_attributes(
            self, "cluster", vpc=self.vpc, cluster_name=APP_NAME, security_groups=[]
        )

    def _create_table(self) -> dynamodb.Table:
        """
        Partition key = server_ip:server_port
        Sort key = game
        """
        return dynamodb.Table(
            self,
            "table",
            table_name=f"{APP_NAME}-{DEPLOYMENT_ENVIRONMENT}",
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=dynamodb.Attribute(
                name="address", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

    def _grant_table_read_write_to_task(self) -> None:
        self.table.grant_read_write_data(self.task.task.task_role)

    def _create_security_group(self) -> ec2.ISecurityGroup:
        security_group_config = SecurityGroupConfig(
            name=f"{APP_NAME}-master-sg",
            vpc=self.vpc,
            ingress=[
                SecurityGroupRule(
                    peer=ec2.Peer.any_ipv4(),
                    connection=ec2.Port.udp(MASTER_PORT),
                    description="Allow master access from anywhere",
                ),
                SecurityGroupRule(
                    peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
                    connection=ec2.Port.tcp(MASTER_HEALTHCHECK_PORT),
                    description="Allow healthcheck from the vpc",
                ),
            ],
        )
        security_group = SecurityGroup(self, security_group_config)
        return security_group

    def _create_service(self) -> ecs.FargateService:
        """
        Create service
        """
        return ecs.FargateService(
            self,
            "service",
            service_name=f"{APP_NAME}-{DEPLOYMENT_ENVIRONMENT}",
            cluster=self.cluster,
            task_definition=self.task.task,
            assign_public_ip=True,
            security_groups=[self._create_security_group()],
            capacity_provider_strategies=[
                ecs.CapacityProviderStrategy(capacity_provider="FARGATE_SPOT"),
            ],
        )

    def _create_network_load_balancer(self) -> elb.NetworkLoadBalancer:
        """
        Create Network Load Balancer
        """
        # TODO: Move to Infra
        return elb.NetworkLoadBalancer(
            self,
            "nlb",
            vpc=self.vpc,
            internet_facing=True,
            cross_zone_enabled=True,
            load_balancer_name=f"{APP_NAME}-{DEPLOYMENT_ENVIRONMENT}",
        )

    def _create_listener(self) -> elb.NetworkListener:
        return self.nlb.add_listener(
            "udplistener", port=MASTER_PORT, protocol=elb.Protocol.UDP
        )

    def _create_service_and_nlb(self) -> None:
        service = self._create_service()
        listener = self._create_listener()

        nlb_healthcheck = elb.HealthCheck(
            port=str(MASTER_HEALTHCHECK_PORT), protocol=elb.Protocol.HTTP
        )

        target = ecs.EcsTarget(
            container_name=f"{APP_NAME}-{DEPLOYMENT_ENVIRONMENT}",
            container_port=MASTER_PORT,
            protocol=ecs.Protocol.UDP,
            new_target_group_id=f"{APP_NAME}-{DEPLOYMENT_ENVIRONMENT}",
            listener=ecs.ListenerConfig.network_listener(
                listener,
                port=MASTER_PORT,
                preserve_client_ip=True,
                health_check=nlb_healthcheck,
            ),
        )

        service.register_load_balancer_targets(target)

    def _create_a_record(self) -> None:
        """
        Create Route53 entries
        """
        Record(
            self,
            zone=None,
            domain=DOMAIN_NAME,
            record_type=route53.RecordType.A,
            record_name="master",
            record_target=self._network_loadbalancer_target(),
        )

    def _network_loadbalancer_target(self) -> route53.RecordTarget:
        return route53.RecordTarget.from_alias(
            route53_targets.LoadBalancerTarget(self.nlb)
        )
