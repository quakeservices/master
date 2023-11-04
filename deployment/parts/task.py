from dataclasses import dataclass
from typing import Literal

from aws_cdk import Duration, RemovalPolicy, Stack
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_logs as logs
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct


@dataclass
class PortConfiguration:
    port: int
    protocol: str


class HealthCheck(PortConfiguration):
    scheme: Literal["http", "https"]
    host: str = "localhost"
    path: str | None = None
    command: list[str] | None = None

    def __post_init__(self) -> None:
        if self.command is None:
            url: str = f"{self.scheme}://{self.host}:{self.port}"

            if self.path:
                url = f"{url}/{self.path}"

            self.command = ["CMD", "curl", "-f", url]


class FargateTask(Construct):
    task: ecs.FargateTaskDefinition
    name: str
    deployment_environment: str
    ports: list[PortConfiguration]
    healtcheck: HealthCheck
    cpu: int
    memory: int
    platform: ecs.RuntimePlatform
    timeout: Duration = Duration.seconds(15)

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        name: str,
        ports: list[PortConfiguration],
        healthcheck: HealthCheck,
        deployment_environment: str,
        cpu: int,
        memory: int,
        arch: "x86_64",
        family: "LINUX",
    ) -> None:
        super().__init__(scope, construct_id)
        self.name = name
        self.deployment_environment = deployment_environment
        self.ports = ports
        self.healthcheck = healthcheck
        self.cpu = cpu
        self.memory = memory
        self.platform = self._platform(arch, family)

        self.credentials = self._credentials()
        self.create()

    def create(self) -> None:
        self.task = ecs.FargateTaskDefinition(
            self,
            "task",
            memory_limit_mib=self.memory,
            cpu=self.cpu,
            runtime_platform=self.platform,
        )
        self._grant_credentials_read_to_task()
        self._container()

    def _container(self) -> None:
        """
        Create container
        """

        container = self.task.add_container(
            "master",
            container_name=f"{self.name}-{self.deployment_environment}",
            image=self._container_image(),
            health_check=self._healtcheck(),
            start_timeout=self.timeout,
            stop_timeout=self.timeout,
            logging=self._logging(),
            memory_reservation_mib=self.memory,
            environment=self._environment,
        )

        for port in self.ports:
            container.add_port_mappings(self._port_mapping(port))

        container.add_port_mappings(self._port_mapping(self.healthcheck))

    def _credentials(self) -> secretsmanager.ISecret:
        return secretsmanager.Secret.from_secret_name_v2(
            self, "ghcr", secret_name=f"{self.name}/github"
        )

    def _container_image(self) -> ecs.ContainerImage:
        return ecs.ContainerImage.from_registry(
            "ghcr.io/quakeservices/master:latest",
            credentials=self.credentials,
        )

    def _grant_credentials_read_to_task(self) -> None:
        execution_role: iam.IRole | None = self.task.execution_role
        if not execution_role:
            execution_role = self.task.obtain_execution_role()

        self.credentials.grant_read(execution_role)

    def _logging(self) -> ecs.LogDriver:
        return ecs.LogDrivers.aws_logs(
            stream_prefix=f"{self.name}-{self.deployment_environment}",
            log_retention=logs.RetentionDays.TWO_WEEKS,
        )

    def _healthcheck(self) -> ecs.HealthCheck:
        return ecs.HealthCheck(command=self.healthcheck.command)

    @staticmethod
    def _port_mapping(config: PortConfiguration) -> ecs.PortMapping:
        return ecs.PortMapping(
            container_port=config.port,
            protocol=getattr(ecs.Protocol, config.protocol.upper()),
        )

    @property
    def _environment(self) -> dict[str, str]:
        return {"DEPLOYMENT_ENVIRONMENT": self.deployment_environment}

    @classmethod
    def _platform(cls, arch: str, family: str) -> ecs.RuntimePlatform:
        return ecs.RuntimePlatform(
            cpu_architecture=cls._arch(arch),
            operating_system_family=cls._family(family),
        )

    @staticmethod
    def _arch(arch: str) -> ecs.CpuArchitecture:
        return getattr(ecs.CpuArchitecture, arch)

    @staticmethod
    def _family(family: str) -> ecs.OperatingSystemFamily:
        return getattr(ecs.OperatingSystemFamily, family)
