from aws_cdk import core
from aws_cdk.aws_iam import PolicyStatement, ManagedPolicy

import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_elasticloadbalancingv2 as elb
import aws_cdk.aws_autoscaling as autoscaling


class MasterDeployStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        master_port = 27900
        master_healthcheck = '8080'

        """
        Gather shared resourcs
        """
        self.vpc = ec2.Vpc.from_lookup(self, 'VPC', vpc_id='vpc-020d0618ebad0cdeb')
        self.ecr = ecr.Repository.from_repository_name(self, 'ECR', 'ecrst-quake-v3hdrh4qq3e0')

        """
        Create Cluster
        """

        self.cluster = ecs.Cluster(self, 'QuakeServices',
                                   cluster_name='QuakeServicesECS',
                                   vpc=self.vpc)

        self.cluster.add_capacity('DefaultAutoScalingGroupCapacity',
                                  instance_type=ec2.InstanceType('t3.micro'),
                                  desired_capacity=1,
                                  max_capacity=6,
                                  min_capacity=1)

        """
        Create task
        """
        task = ecs.Ec2TaskDefinition(self, 'QuakeMasterTask',
            network_mode=ecs.NetworkMode.HOST)

        policy = PolicyStatement(
            resources=["*"],
            actions=["dynamodb:Create*",
                     "dynamodb:Delete*",
                     "dynamodb:Get*",
                     "dynamodb:PutItem",
                     "dynamodb:Query",
                     "dynamodb:Scan",
                     "dynamodb:Update*",
                     "dynamodb:Describe*",
                     "dynamodb:List*"])

        task.add_to_task_role_policy(policy)

        """
        Create container
        """

        container = task.add_container('Master',
            image=ecs.ContainerImage.from_ecr_repository(self.ecr, tag='latest'),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="Master"),
            memory_reservation_mib=256)

        container_port_udp = ecs.PortMapping(container_port=master_port,
                                             protocol=ecs.Protocol.UDP)
        container_port_tcp = ecs.PortMapping(container_port=master_port,
                                             protocol=ecs.Protocol.TCP)
        container_hc_tcp = ecs.PortMapping(container_port=80,
                                           protocol=ecs.Protocol.TCP)

        container.add_port_mappings(container_port_udp)
        container.add_port_mappings(container_port_tcp)
        container.add_port_mappings(container_hc_tcp)

        """
        Create service
        """
        service = ecs.Ec2Service(self, 'QuakeMasterService',
            cluster=self.cluster,
            task_definition=task)

        """
        Create Network Load Balancer
        """
        lb = elb.NetworkLoadBalancer(self, 'QuakeServicesNLB',
            vpc=self.vpc,
            internet_facing=True,
            cross_zone_enabled=True)

        listener = lb.add_listener('Listener',
            port=master_port,
            protocol=elb.Protocol.UDP)

        healthcheck = elb.HealthCheck(port='80', protocol=elb.Protocol.HTTP)

        listener.add_targets('ECS',
            port=master_port,
            targets=[service],
            proxy_protocol_v2=True,
            health_check=healthcheck)
