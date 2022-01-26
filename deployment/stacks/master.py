import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_elasticloadbalancingv2 as elb
import aws_cdk.aws_iam as iam
import aws_cdk.aws_logs as logs
import aws_cdk.aws_route53 as route53
import aws_cdk.aws_route53_targets as route53_targets
import boto3
from aws_cdk import core as cdk


class MasterDeployStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.master_port = 27900
        self.master_healthcheck_port = 8080

        self.vpc, self.cluster = self.gather_shared_resources()

        self.table = dynamodb.Table.from_table_name(self, "server", "server")

        self.task = self.create_master_task()
        self.container = self.create_task_container()
        self.nlb = self.create_network_load_balancer()
        self.create_service_and_nlb()
        self.create_route53_record()

    def create_table(self):
        return dynamodb.Table(
            self,
            "server-table",
            partition_key=dynamodb.Attribute(
                name="address", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="game", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

    def create_master_task(self):
        """
        Create master task
        """
        task = ecs.FargateTaskDefinition(self, "task", memory_limit_mib=512, cpu=256)

        task.add_to_task_role_policy(self.create_dynamodb_access_policy())
        task.add_to_task_role_policy(self.create_xray_access_policy())

        return task

    def create_dynamodb_access_policy(self):
        return iam.PolicyStatement(
            resources=[self.table.table_arn],
            actions=[
                "dynamodb:BatchGetItem",
                "dynamodb:GetRecords",
                "dynamodb:GetShardIterator",
                "dynamodb:Query",
                "dynamodb:GetItem",
                "dynamodb:Scan",
                "dynamodb:BatchWriteItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:DescribeTable",
            ],
        )

    def create_xray_access_policy(self):
        return iam.PolicyStatement(
            resources=["*"],
            actions=[
                "xray:GetGroup",
                "xray:GetGroups",
                "xray:GetSampling*",
                "xray:GetTime*",
                "xray:GetService*",
                "xray:PutTelemetryRecords",
                "xray:PutTraceSegments",
            ],
        )

    def define_container_image(self):
        master_ecr = ecr.Repository.from_repository_name(
            self, "ECR", "quakeservices_master"
        )

        return ecs.ContainerImage.from_ecr_repository(master_ecr, tag="latest")

    def create_task_container(self):
        """
        Create container
        """
        ecs_healthcheck = ecs.HealthCheck(
            command=["CMD", "curl", "-f", "http://localhost:8080"]
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
            memory_reservation_mib=256,
        )

        container.add_port_mappings(
            ecs.PortMapping(container_port=self.master_port, protocol=ecs.Protocol.UDP)
        )
        container.add_port_mappings(
            ecs.PortMapping(
                container_port=self.master_healthcheck_port, protocol=ecs.Protocol.TCP
            )
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

    def create_listener(self):
        return self.nlb.add_listener(
            "UDPListener", port=self.master_port, protocol=elb.Protocol.UDP
        )

    def create_service_and_nlb(self):
        service = self.create_service()
        listener = self.create_listener()

        nlb_healthcheck = elb.HealthCheck(
            port=str(self.master_healthcheck_port), protocol=elb.Protocol.HTTP
        )

        listener.add_targets(
            "ECS",
            port=self.master_port,
            targets=[
                service.load_balancer_target(
                    container_name="master",
                    container_port=self.master_port,
                    protocol=ecs.Protocol.UDP,
                )
            ],
            proxy_protocol_v2=True,
            health_check=nlb_healthcheck,
        )

        # self.add_udp_overrides(listener, target_group)

    def add_udp_overrides(self, listener, target_group):
        """
        At the time of writing Protocol would be set to TCP without these overrides
        """
        # Required overrides as Protocol never gets set correctly
        cfn_listener = listener.node.default_child
        cfn_listener.add_override("Properties.Protocol", "UDP")

        # Required overrides as Protocol never gets set correctly
        cfn_target_group = target_group.node.default_child
        cfn_target_group.add_override("Properties.Protocol", "UDP")

    def create_route53_record(self):
        """
        Create Route53 entries
        """
        zone = route53.HostedZone.from_lookup(
            self, "quake_services", domain_name="quake.services"
        )

        target = route53.AddressRecordTarget.from_alias(
            route53_targets.LoadBalancerTarget(self.nlb)
        )

        route53.ARecord(self, "alias", zone=zone, record_name="master", target=target)

    def gather_shared_resources(self):
        client = boto3.client("ssm", region_name="ap-southeast-2")
        r = client.get_parameter(Name="/common/shared_vpc_id")
        if "Parameter" in r.keys():
            vpc_id = r["Parameter"]["Value"]

        vpc = ec2.Vpc.from_lookup(self, "SharedVPC", vpc_id=vpc_id)

        cluster = ecs.Cluster.from_cluster_attributes(
            self, "ECS", cluster_name="SharedECSCluster", vpc=vpc, security_groups=[]
        )

        return vpc, cluster
