from typing import Any

from aws_cdk import Stage
from constructs import Construct

from deployment.constants import APP_NAME
from deployment.stacks import InfraStack, MasterStack, WebBackendStack, WebFrontendStack


class PipelineInfraStage(Stage):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        deployment_environment: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        InfraStack(self, deployment_environment)


class PipelineMasterStage(Stage):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        deployment_environment: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        MasterStack(self, deployment_environment)


class PipelineWebBackendStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)

        WebBackendStack(self, f"{APP_NAME}-backend")


class PipelineWebFrontendStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)

        WebFrontendStack(self, f"{APP_NAME}-frontend")
