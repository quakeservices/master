from typing import Any, Literal

from aws_cdk import Duration
from aws_cdk import aws_ecs as ecs

from deployment.models.base import DeploymentBaseModel
from deployment.models.network.ports import PortConfiguration


class EcsHealthCheckConfiguration(PortConfiguration):
    scheme: Literal["http", "https"]
    host: str = "localhost"
    path: str | None = None
    command: list[str] | None = None
    interval: Duration = Duration.seconds(30)
    retries: int = 3
    start_period: Duration | None = None
    timeout: Duration = Duration.seconds(5)

    def model_post_init(self, __context: Any) -> None:
        if self.command is None:
            self._build_command()

    def _build_command(self) -> None:
        url: str = f"{self.scheme}://{self.host}:{self.port}"

        if self.path:
            url = f"{url}/{self.path}"

        self.command = ["CMD", "curl", "-f", url]

    @property
    def as_cdk_object(self) -> ecs.HealthCheck:
        return ecs.HealthCheck(command=self.command)


class RegistryConfiguration(DeploymentBaseModel):
    name: Literal["ghcr", "ecr"]
    namespace: str
    image: str
    tag: str = "latest"
    region: str | None = None

    def model_post_init(self, __context: Any) -> None:
        self.image_path = f"{self.namespace}/{self.image}:{self.tag}"

        if self.name == "ecr" and self.region is None:
            raise ValueError("Region is required for ECR registry")

    @property
    def uri(self) -> str:
        return self._build_uri()

    def _build_uri(self) -> str:
        match self.name:
            case "ghcr":
                return self._build_uri_ghcr()
            case "ecr":
                return self._build_uri_ecr()
            case _:
                raise ValueError(f"Unknown registry name: {self.name}")

    def _build_uri_ghcr(self) -> str:
        return f"ghcr.io/{self.image_path}"

    def _build_uri_ecr(self) -> str:
        return f"{self.name}.dkr.ecr.{self.region}.amazonaws.com/{self.image_path}"


class FargateTaskConfiguration(DeploymentBaseModel):
    name: str
    ports: list[PortConfiguration]
    healthcheck: EcsHealthCheck
    deployment_environment: str
    registry: RegistryConfiguration
    cpu: int
    memory: int
    arch: str = "x86_64"
    family: str = "LINUX"
    platform: ecs.RuntimePlatform | None = None
    timeout: Duration = Duration.seconds(15)

    def model_post_init(self, __context: Any) -> None:
        if self.platform is None:
            self.platform = self._platform()

    def _platform(self) -> ecs.RuntimePlatform:
        return ecs.RuntimePlatform(
            cpu_architecture=self._arch(self.arch),
            operating_system_family=self._family(self.family),
        )

    @staticmethod
    def _arch(arch: str) -> ecs.CpuArchitecture:
        value: ecs.CpuArchitecture = ecs.CpuArchitecture.X86_64
        if hasattr(ecs.CpuArchitecture, arch):
            value = getattr(ecs.CpuArchitecture, arch)

        return value

    @staticmethod
    def _family(family: str) -> ecs.OperatingSystemFamily:
        value: ecs.OperatingSystemFamily = ecs.OperatingSystemFamily.LINUX
        if hasattr(ecs.OperatingSystemFamily, family):
            value = getattr(ecs.OperatingSystemFamily, family)

        return value
