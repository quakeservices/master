from aws_cdk import core

import aws_cdk.aws_iam as iam
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecs as ecs


class XrayDeployStack(core.Stack):

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 vpc_id,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.vpc, self.cluster = self.gather_shared_resources(vpc_id)

        """
        Create X-Ray task container
        """
        xray_task = ecs.Ec2TaskDefinition(
            self,
            'task',
            network_mode=ecs.NetworkMode.HOST
        )

        xray_policy = iam.PolicyStatement(
            resources=["*"],
            actions=[
                "xray:GetGroup",
                "xray:GetGroups",
                "xray:GetSampling*",
                "xray:GetTime*",
                "xray:GetService*",
                "xray:PutTelemetryRecords",
                "xray:PutTraceSegments"
            ]
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

        service = ecs.Ec2Service(
            self,
            'XRayService',
            cluster=self.cluster,
            task_definition=xray_task,
            daemon=True
        )

    def gather_shared_resources(self, vpc_id):
        vpc = ec2.Vpc.from_lookup(
            self,
            'SharedVPC',
            vpc_id=vpc_id
        )

        cluster = ecs.Cluster.from_cluster_attributes(
            self,
            'ECS',
            cluster_name='SharedECSCluster',
            vpc=vpc,
            security_groups=[]
        )

        return vpc, cluster
