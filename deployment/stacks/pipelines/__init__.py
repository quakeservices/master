from aws_cdk import Stage
from constructs import Construct

from deployment.constants import APP_NAME
from deployment.stacks import InfraStack, MasterStack, WebBackendStack, WebFrontendStack


class PipelineInfraStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        InfraStack(self, f"{APP_NAME}-infra")


class PipelineMasterStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        MasterStack(self, f"{APP_NAME}-master")


class PipelineWebBackendStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        WebBackendStack(self, f"{APP_NAME}-backend")


class PipelineWebFrontendStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        WebFrontendStack(self, f"{APP_NAME}-frontend")
