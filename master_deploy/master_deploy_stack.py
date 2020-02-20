from aws_cdk import core
from aws_cdk.aws_iam import PolicyStatement, ManagedPolicy

import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_elasticloadbalancingv2 as elb
import aws_cdk.aws_autoscaling as autoscaling
import aws_cdk.aws_route53 as route53
import aws_cdk.aws_route53_targets as route53_targets


class MasterDeployStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        cluster_size = 2
        master_port = 27900
        master_healthcheck = '8080'

        """
        Gather shared resourcs
        """
        self.vpc = ec2.Vpc.from_lookup(self, 'VPC', vpc_id='vpc-020d0618ebad0cdeb')
        self.ecr = ecr.Repository.from_repository_name(self, 'ECR', 'ecrst-quake-v3hdrh4qq3e0')
        self.zone = route53.HostedZone.from_lookup(self, "quake_services", domain_name="quake.services")


        """
        Create Cluster
        """

        self.cluster = ecs.Cluster(self,
                                   'QuakeServices',
                                   cluster_name='QuakeServicesECS',
                                   vpc=self.vpc)

        self.cluster.add_capacity('DefaultAutoScalingGroupCapacity',
                                  instance_type=ec2.InstanceType('t3.nano'),
                                  desired_capacity=cluster_size,
                                  max_capacity=6,
                                  min_capacity=1,
                                  task_drain_time=core.Duration.minutes(1))

        """
        Create master task
        """
        task = ecs.Ec2TaskDefinition(self,
                                     'QuakeMasterTask',
                                     network_mode=ecs.NetworkMode.HOST)

        policy = PolicyStatement(
            resources=["*"],
            actions=["dynamodb:BatchGetItem",
                     "dynamodb:GetRecords",
                     "dynamodb:GetShardIterator",
                     "dynamodb:Query",
                     "dynamodb:GetItem",
                     "dynamodb:Scan",
                     "dynamodb:BatchWriteItem",
                     "dynamodb:PutItem",
                     "dynamodb:UpdateItem",
                     "dynamodb:DeleteItem"]
        )

        task.add_to_task_role_policy(policy)

        """
        Create X-Ray task container
        """
        xray_task = ecs.Ec2TaskDefinition(self,
                                     'xray-daemon-task',
                                     network_mode=ecs.NetworkMode.HOST)

        xray = xray_task.add_container('xray-daemon',
            start_timeout=core.Duration.seconds(60),
            stop_timeout=core.Duration.seconds(60),
            image=ecs.ContainerImage.from_registry('amazon/aws-xray-daemon'),
            memory_reservation_mib=256)

        xray_port_udp = ecs.PortMapping(container_port=2000,
                                        protocol=ecs.Protocol.UDP)

        xray.add_port_mappings(xray_port_udp)


        """
        Create container
        """
        ecs_healthcheck = ecs.HealthCheck(command=["CMD", "curl", "-f", "http://localhost:8080"])

        container = task.add_container('Master',
            hostname='master',
            health_check=ecs_healthcheck,
            start_timeout=core.Duration.seconds(15),
            stop_timeout=core.Duration.seconds(15),
            image=ecs.ContainerImage.from_ecr_repository(self.ecr, tag='latest'),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="Master"),
            memory_reservation_mib=256)

        container_port_udp = ecs.PortMapping(container_port=master_port,
                                             protocol=ecs.Protocol.UDP)
        container_hc_tcp = ecs.PortMapping(container_port=8080,
                                           protocol=ecs.Protocol.TCP)

        container.add_port_mappings(container_port_udp)
        container.add_port_mappings(container_hc_tcp)

        """
        Create service
        """
        service = ecs.Ec2Service(self, 'QuakeMasterService',
            cluster=self.cluster,
            task_definition=task,
            desired_count=cluster_size,
            placement_strategies=[ecs.PlacementStrategy.spread_across_instances()])

        """
        Create Network Load Balancer
        """
        lb = elb.NetworkLoadBalancer(self, 'QuakeServicesNLB',
            vpc=self.vpc,
            internet_facing=True,
            cross_zone_enabled=True,
            load_balancer_name='master')

        listener = lb.add_listener('UDPListener',
            port=master_port,
            protocol=elb.Protocol.UDP)

        # Required overrides as Protocol never gets set correctly
        cfn_listener = listener.node.default_child
        cfn_listener.add_override("Properties.Protocol", "UDP")

        elb_healthcheck = elb.HealthCheck(port='8080',
                                          protocol=elb.Protocol.HTTP)

        target_group = listener.add_targets('ECS',
                                            port=master_port,
                                            targets=[service.load_balancer_target(
                                                container_name='Master',
                                                container_port=master_port,
                                                protocol=ecs.Protocol.UDP)],
                                            proxy_protocol_v2=True,
                                            health_check=elb_healthcheck)

        # Required overrides as Protocol never gets set correctly
        cfn_target_group = target_group.node.default_child
        cfn_target_group.add_override("Properties.Protocol", "UDP")

        """
        Create Route53 entries
        """
        route53.ARecord(self, "Alias",
            zone=self.zone,
            record_name='master',
            target=route53.AddressRecordTarget.from_alias(route53_targets.LoadBalancerTarget(lb))
        )
