from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct

from deployment.models.task import FargateTaskConfiguration, PortConfiguration


class FargateTask(Construct):
    task: ecs.FargateTaskDefinition
    config: FargateTaskConfiguration

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: FargateTaskConfiguration,
    ) -> None:
        super().__init__(scope, construct_id)

        self.config = config
        self.create()

    def create(self) -> None:
        self.credentials = self._credentials()
        self.task = ecs.FargateTaskDefinition(
            self,
            "task",
            memory_limit_mib=self.config.memory,
            cpu=self.config.cpu,
            runtime_platform=self.config.platform,
        )
        self._grant_credentials_read_to_task()
        self._container()

    def _container(self) -> None:
        """
        Create container
        """

        container = self.task.add_container(
            self.config.name,
            container_name=f"{self.config.name}-{self.config.deployment_environment}",
            image=self._container_image(),
            health_check=self.config.healthcheck.as_cdk_object,
            start_timeout=self.config.timeout,
            stop_timeout=self.config.timeout,
            logging=self._logging(),
            memory_reservation_mib=self.config.memory,
            environment=self._environment,
        )

        for port in self.config.ports:
            container.add_port_mappings(self._port_mapping(port))

        container.add_port_mappings(self._port_mapping(self.config.healthcheck))

    def _credentials(self) -> secretsmanager.ISecret:
        return secretsmanager.Secret.from_secret_name_v2(
            self, self.config.registry.name, secret_name=f"{self.config.name}/github"
        )

    def _container_image(self) -> ecs.ContainerImage:
        return ecs.ContainerImage.from_registry(
            self.config.registry.uri,
            credentials=self.credentials,
        )

    def _grant_credentials_read_to_task(self) -> None:
        execution_role: iam.IRole | None = self.task.execution_role
        if not execution_role:
            execution_role = self.task.obtain_execution_role()

        self.credentials.grant_read(execution_role)

    def _logging(self) -> ecs.LogDriver:
        return ecs.LogDrivers.aws_logs(
            stream_prefix=f"{self.config.name}-{self.config.deployment_environment}",
            log_retention=logs.RetentionDays.TWO_WEEKS,
        )

    @staticmethod
    def _port_mapping(config: PortConfiguration) -> ecs.PortMapping:
        return ecs.PortMapping(
            container_port=config.port,
            protocol=getattr(ecs.Protocol, config.protocol.upper()),
        )

    @property
    def _environment(self) -> dict[str, str]:
        return {"DEPLOYMENT_ENVIRONMENT": self.config.deployment_environment}
