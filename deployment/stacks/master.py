from aws_cdk import Duration, Stack
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from aws_cdk import aws_ssm as ssm
from constructs import Construct
from deployment.constants import APP_NAME, DOMAIN_NAME


class MasterStack(Stack):
    MASTER_PORT: int = 27900
    MASTER_HEALTHCHECK_PORT: int = 8080
    MASTER_CPU: int = 256
    MASTER_MEMORY: int = 512
    DEFAULT_TIMEOUT: int = 15

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = self._get_vpc()
        self.zone = self._get_zone()
        self.cluster = self._get_cluster()
        self.table = self._get_table()

        self.task = self._create_master_task()
        self.container = self._create_task_container()
        self.nlb = self._create_network_load_balancer()
        self._create_service_and_nlb()
        self._create_route53_record()

    def _get_vpc(self) -> ec2.Vpc:
        return ec2.Vpc.from_lookup(self, "vpc", vpc_name=APP_NAME)

    def _get_zone(self) -> route53.HostedZone:
        return route53.HostedZone.from_lookup(self, "domain", domain_name=DOMAIN_NAME)

    def _get_cluster(self) -> ecs.Cluster:
        return ecs.Cluster.from_cluster_attributes(
            self, "cluster", vpc=self.vpc, cluster_name=APP_NAME, security_groups=[]
        )

    def _get_ecr_repository(self) -> ecr.Repository:
        return ecr.Repository.from_repository_name(
            self, "repository", repository_name=APP_NAME
        )

    def _get_table(self) -> dynamodb.Table:
        return dynamodb.Table.from_table_name(
            self,
            "table",
            table_name=APP_NAME,
        )

    def _create_master_task(self) -> ecs.FargateTaskDefinition:
        """
        Create master task
        """
        task = ecs.FargateTaskDefinition(
            self, "task", memory_limit_mib=self.MASTER_MEMORY, cpu=self.MASTER_CPU
        )
        self.table.grant_read_write_data(task)

        return task

    def _define_container_image(self) -> ecs.ContainerImage:
        master_ecr = ecr.Repository.from_repository_name(self, "ECR", APP_NAME)

        return ecs.ContainerImage.from_ecr_repository(master_ecr, tag="latest")

    def _create_task_container(self) -> ecs.ContainerDefinition:
        """
        Create container
        """
        ecs_healthcheck = ecs.HealthCheck(
            command=[
                "CMD",
                "curl",
                "-f",
                f"http://localhost:{self.MASTER_HEALTHCHECK_PORT}",
            ]
        )

        log_settings = ecs.LogDrivers.aws_logs(
            stream_prefix=APP_NAME,
            log_retention=logs.RetentionDays.TWO_WEEKS,
        )

        container = self.task.add_container(
            "master",
            health_check=ecs_healthcheck,
            start_timeout=Duration.seconds(self.DEFAULT_TIMEOUT),
            stop_timeout=Duration.seconds(self.DEFAULT_TIMEOUT),
            image=self._define_container_image(),
            logging=log_settings,
            memory_reservation_mib=self.MASTER_MEMORY,
        )

        container.add_port_mappings(
            ecs.PortMapping(container_port=self.MASTER_PORT, protocol=ecs.Protocol.UDP)
        )
        container.add_port_mappings(
            ecs.PortMapping(
                container_port=self.MASTER_HEALTHCHECK_PORT, protocol=ecs.Protocol.TCP
            )
        )

        return container

    def _create_service(self):
        """
        Create service
        """
        return ecs.FargateService(
            self,
            "service",
            service_name=APP_NAME,
            cluster=self.cluster,
            task_definition=self.task,
        )

    def _create_network_load_balancer(self) -> elb.NetworkLoadBalancer:
        """
        Create Network Load Balancer
        """
        return elb.NetworkLoadBalancer(
            self,
            "nlb",
            vpc=self.vpc,
            internet_facing=True,
            cross_zone_enabled=True,
            load_balancer_name=APP_NAME,
        )

    def _create_listener(self) -> elb.NetworkListener:
        return self.nlb.add_listener(
            "udplistener", port=self.MASTER_PORT, protocol=elb.Protocol.UDP
        )

    def _create_service_and_nlb(self):
        service = self._create_service()
        listener = self._create_listener()

        nlb_healthcheck = elb.HealthCheck(
            port=str(self.MASTER_HEALTHCHECK_PORT), protocol=elb.Protocol.HTTP
        )

        listener.add_targets(
            "target",
            port=self.MASTER_PORT,
            targets=[
                service.load_balancer_target(
                    container_name=APP_NAME,
                    container_port=self.MASTER_PORT,
                    protocol=ecs.Protocol.UDP,
                )
            ],
            proxy_protocol_v2=True,
            health_check=nlb_healthcheck,
        )

    def _create_route53_record(self):
        """
        Create Route53 entries
        """
        target = route53.AddressRecordTarget.from_alias(
            route53_targets.LoadBalancerTarget(self.nlb)
        )

        route53.ARecord(
            self, "alias", zone=self.zone, record_name="master", target=target
        )
