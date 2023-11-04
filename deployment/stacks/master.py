from typing import Any, Final, Literal, Optional

from aws_cdk import Duration, RemovalPolicy, Stack
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct

from deployment.constants import *
from deployment.parts.record import Record


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
        self.task = self._create_master_task()
        self.credentials = self._get_ghcr_credentials()
        self._grant_credentials_read_to_task()
        self._grant_table_read_write_to_task()
        self._create_task_container()
        self.nlb = self._create_network_load_balancer()
        self._create_service_and_nlb()
        self._create_a_record()

    def _get_vpc(self) -> ec2.IVpc:
        return ec2.Vpc.from_lookup(self, "vpc", vpc_name=APP_NAME)

    def _get_zone(self) -> route53.IHostedZone:
        return route53.HostedZone.from_lookup(self, "domain", domain_name=DOMAIN_NAME)

    def _get_cluster(self) -> ecs.ICluster:
        return ecs.Cluster.from_cluster_attributes(
            self, "cluster", vpc=self.vpc, cluster_name=APP_NAME, security_groups=[]
        )

    def _get_ghcr_credentials(self) -> secretsmanager.ISecret:
        return secretsmanager.Secret.from_secret_name_v2(
            self, "ghcr", secret_name=f"{APP_NAME}/github"
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

    def _create_master_task(self) -> ecs.FargateTaskDefinition:
        """
        Create master task
        """
        return ecs.FargateTaskDefinition(
            self,
            "task",
            memory_limit_mib=MASTER_MEMORY,
            cpu=MASTER_CPU,
            runtime_platform=ecs.RuntimePlatform(
                cpu_architecture=ecs.CpuArchitecture.X86_64,
                operating_system_family=ecs.OperatingSystemFamily.LINUX,
            ),
        )

    def _grant_table_read_write_to_task(self) -> None:
        self.table.grant_read_write_data(self.task.task_role)

    def _grant_credentials_read_to_task(self) -> None:
        execution_role: Optional[iam.IRole] = self.task.execution_role
        if not execution_role:
            execution_role = self.task.obtain_execution_role()

        self.credentials.grant_read(execution_role)

    def _define_container_image(self) -> ecs.ContainerImage:
        return ecs.ContainerImage.from_registry(
            "ghcr.io/quakeservices/master:latest",
            credentials=self.credentials,
        )

    def _create_task_container(self) -> None:
        """
        Create container
        """
        ecs_healthcheck = ecs.HealthCheck(
            command=[
                "CMD",
                "curl",
                "-f",
                f"http://localhost:{MASTER_HEALTHCHECK_PORT}",
            ]
        )

        log_settings = ecs.LogDrivers.aws_logs(
            stream_prefix=f"{APP_NAME}-{DEPLOYMENT_ENVIRONMENT}",
            log_retention=logs.RetentionDays.TWO_WEEKS,
        )

        container = self.task.add_container(
            "master",
            container_name=f"{APP_NAME}-{DEPLOYMENT_ENVIRONMENT}",
            image=self._define_container_image(),
            health_check=ecs_healthcheck,
            start_timeout=Duration.seconds(DEFAULT_TIMEOUT),
            stop_timeout=Duration.seconds(DEFAULT_TIMEOUT),
            logging=log_settings,
            memory_reservation_mib=MASTER_MEMORY,
            environment={"DEPLOYMENT_ENVIRONMENT": DEPLOYMENT_ENVIRONMENT},
        )

        container.add_port_mappings(
            ecs.PortMapping(container_port=MASTER_PORT, protocol=ecs.Protocol.UDP)
        )
        container.add_port_mappings(
            ecs.PortMapping(
                container_port=MASTER_HEALTHCHECK_PORT, protocol=ecs.Protocol.TCP
            )
        )

    def _create_security_group(self) -> ec2.ISecurityGroup:
        security_group = ec2.SecurityGroup(
            self,
            "sg",
            vpc=self.vpc,
            allow_all_outbound=True,
            security_group_name=f"{APP_NAME}-master-sg",
        )

        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.udp(MASTER_PORT),
            "Allow master access from anywhere",
        )
        security_group.add_ingress_rule(
            ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            ec2.Port.tcp(MASTER_HEALTHCHECK_PORT),
            "Allow healthcheck from the vpc",
        )
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
            task_definition=self.task,
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
            "alias",
            domain=DOMAIN_NAME,
            record_type=route53.RecordType.A,
            record_name="master",
            record_target=self._network_loadbalancer_target(),
        )

    def _network_loadbalancer_target(self) -> route53.RecordTarget:
        return route53.RecordTarget.from_alias(
            route53_targets.LoadBalancerTarget(self.nlb)
        )
