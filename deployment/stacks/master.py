from aws_cdk import Stack
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
from aws_cdk import core as cdk
from constructs import Construct
from deployment.constants import APP_NAME, DOMAIN_NAME


class MasterStack(Stack):
    MASTER_PORT = 27900
    MASTER_HEALTHCHECK_PORT = 8080
    MASTER_CPU = 256
    MASTER_MEMORY = 512

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = self._get_vpc()
        self.cluster = self._get_ecs_cluster()
        self.zone = self._get_zone()

        self.table = dynamodb.Table.from_table_name(
            self, "table", table_name="masterserver"
        )

        self.task = self.create_master_task()
        self.container = self.create_task_container()
        self.nlb = self.create_network_load_balancer()
        self.create_service_and_nlb()
        self.create_route53_record()

    def create_master_task(self, memory: int = MASTER_MEMORY, cpu: int = MASTER_CPU):
        """
        Create master task
        """
        task = ecs.FargateTaskDefinition(self, "task", memory_limit_mib=memory, cpu=cpu)

        task.add_to_task_role_policy(self.create_dynamodb_access_policy())

        return task

    def create_dynamodb_access_policy(self):
        return iam.PolicyStatement(
            resources=[self.table.table_arn],
            actions=[
                "dynamodb:BatchGetItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:DeleteItem",
                "dynamodb:DescribeTable",
                "dynamodb:GetItem",
                "dynamodb:GetRecords",
                "dynamodb:GetShardIterator",
                "dynamodb:PutItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:UpdateItem",
            ],
        )

    def define_container_image(self):
        master_ecr = ecr.Repository.from_repository_name(
            self, "ECR", "quakeservices_master"
        )

        return ecs.ContainerImage.from_ecr_repository(master_ecr, tag="latest")

    def create_task_container(
        self,
        memory: int = MASTER_MEMORY,
        port_master: int = MASTER_PORT,
        port_check: int = MASTER_HEALTHCHECK_PORT,
    ):
        """
        Create container
        """
        ecs_healthcheck = ecs.HealthCheck(
            command=["CMD", "curl", "-f", f"http://localhost:{port_check}"]
        )

        log_settings = ecs.LogDrivers.aws_logs(
            stream_prefix="master",
            log_retention=logs.RetentionDays.TWO_WEEKS,
        )

        container = self.task.add_container(
            "master",
            health_check=ecs_healthcheck,
            start_timeout=cdk.Duration.seconds(15),
            stop_timeout=cdk.Duration.seconds(15),
            image=self.define_container_image(),
            logging=log_settings,
            memory_reservation_mib=memory,
        )

        container.add_port_mappings(
            ecs.PortMapping(container_port=port_master, protocol=ecs.Protocol.UDP)
        )
        container.add_port_mappings(
            ecs.PortMapping(container_port=port_check, protocol=ecs.Protocol.TCP)
        )

        return container

    def create_service(self):
        """
        Create service
        """
        return ecs.FargateService(
            self, "service", cluster=self.cluster, task_definition=self.task
        )

    def create_network_load_balancer(self):
        """
        Create Network Load Balancer
        """
        return elb.NetworkLoadBalancer(
            self,
            "nlb",
            vpc=self.vpc,
            internet_facing=True,
            cross_zone_enabled=True,
            load_balancer_name="master",
        )

    def create_listener(self, port_master: int = MASTER_PORT):
        return self.nlb.add_listener(
            "UDPListener", port=port_master, protocol=elb.Protocol.UDP
        )

    def create_service_and_nlb(
        self, port_master: int = MASTER_PORT, port_check: int = MASTER_HEALTHCHECK_PORT
    ):
        service = self.create_service()
        listener = self.create_listener()

        nlb_healthcheck = elb.HealthCheck(
            port=str(port_check), protocol=elb.Protocol.HTTP
        )

        listener.add_targets(
            "ECS",
            port=port_master,
            targets=[
                service.load_balancer_target(
                    container_name="master",
                    container_port=port_master,
                    protocol=ecs.Protocol.UDP,
                )
            ],
            proxy_protocol_v2=True,
            health_check=nlb_healthcheck,
        )

    def create_route53_record(self):
        """
        Create Route53 entries
        """
        target = route53.AddressRecordTarget.from_alias(
            route53_targets.LoadBalancerTarget(self.nlb)
        )

        route53.ARecord(
            self, "alias", zone=self.zone, record_name="master", target=target
        )

    def _get_vpc(self, path: str = "/common/shared_vpc_id"):
        vpc_id = ssm.StringParameter.value_from_lookup(self, path)
        return ec2.Vpc.from_lookup(self, "SharedVPC", vpc_id=vpc_id)

    def _get_ecs_cluster(self):
        return ecs.Cluster.from_cluster_attributes(
            self,
            "ecs-cluster",
            cluster_name="SharedECSCluster",
            vpc=self.vpc,
            security_groups=[],
        )

    def _get_zone(self, domain: str = "quake.services"):
        return route53.HostedZone.from_lookup(
            self, "quake_services", domain_name=domain
        )
