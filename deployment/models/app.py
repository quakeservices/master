from deployment.models.base import DeploymentBaseModel
from deployment.models.fargate.task import EcsHealthCheckConfiguration
from deployment.models.network.ports import PortConfiguration


class AppDeploymentConfig(DeploymentBaseModel):
    deployment_environment: str


class AppNetworkConfig(DeploymentBaseModel):
    ports: list[PortConfiguration] | None
    health_check: EcsHealthCheckConfiguration | None


class AppDnsConfig(DeploymentBaseModel):
    primary_domain: str
    auxiliary_domains: list[str]


class AppConfig(DeploymentBaseModel):
    name: str
    deployment: AppDeploymentConfig
    network: AppNetworkConfig
    dns: AppDnsConfig
