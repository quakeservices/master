from aws_cdk import core
from aws_cdk.aws_iam import PolicyStatement, ManagedPolicy

import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_ec2 as ec2


class XrayDeployStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        """
        Gather shared resourcs
        """
        self.vpc = ec2.Vpc.from_lookup(self, 'VPC', vpc_id='vpc-020d0618ebad0cdeb')
        self.sg = ec2.SecurityGroup.from_security_group_id(self, 'SecurityGroup', security_group_id='sg-00f092d1351e01713')
        self.cluster = ecs.Cluster.from_cluster_attributes(self, 'ECS', cluster_name='QuakeServicesECS', vpc=self.vpc, security_groups=[self.sg])

        """
        Create X-Ray task container
        """
        xray_task = ecs.Ec2TaskDefinition(
            self,
            'xray-daemon-task',
            network_mode=ecs.NetworkMode.HOST
        )

        xray_policy = PolicyStatement(
            resources=["*"],
            actions=["xray:GetGroup",
                     "xray:GetGroups",
                     "xray:GetSampling*",
                     "xray:GetTime*",
                     "xray:GetService*",
                     "xray:PutTelemetryRecords",
                     "xray:PutTraceSegments"]
        )

        xray_task.add_to_task_role_policy(xray_policy)

        xray = xray_task.add_container(
            'xray-daemon',
            start_timeout=core.Duration.seconds(60),
            stop_timeout=core.Duration.seconds(60),
            image=ecs.ContainerImage.from_registry('amazon/aws-xray-daemon'),
            memory_reservation_mib=256
        )

        xray_port_udp = ecs.PortMapping(
            container_port=2000,
            protocol=ecs.Protocol.UDP
        )
        xray_port_tcp = ecs.PortMapping(
            container_port=2000,
            protocol=ecs.Protocol.TCP
        )

        xray.add_port_mappings(xray_port_udp)
        xray.add_port_mappings(xray_port_tcp)

        service = ecs.Ec2Service(self, 'XRayService',
            cluster=self.cluster,
            task_definition=xray_task,
            daemon=True
        )
