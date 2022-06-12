from aws_cdk import RemovalPolicy, Stack, Stage
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from constructs import Construct
from deployment.constants import APP_NAME, DOMAINS, REPO
from deployment.environments import us_east_1, us_west_2
from deployment.stacks.infra import InfraStack
from deployment.stacks.master import MasterStack
from deployment.stacks.web_backend import WebBackendStack
from deployment.stacks.web_frontend import WebFrontendStack


class PipelineStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.pipeline = self._create_pipeline()

    def _create_pipeline(self):
        return CodePipeline(
            self,
            "pipeline",
            pipeline_name=APP_NAME,
            synth=ShellStep(
                "Synth",
                input=CodePipelineSource.git_hub(REPO, "main"),
                commands=[
                    "npm install -g aws-cdk",
                    "python -m pip install -r deployment/requirements.txt",
                    "cdk synth",
                ],
            ),
        )

    def _create_infra_stage(self):
        self.pipeline.add_stage(PipelineInfraStage(self, "infra", env=us_west_2))

    def _create_master_stage(self):
        self.pipeline.add_stage(PipelineMasterStage(self, "master", env=us_west_2))

    def _create_web_backend_stage(self):
        self.pipeline.add_stage(PipelineMasterStage(self, "web_backend", env=us_west_2))

    def _create_web_frontend_stage(self):
        self.pipeline.add_stage(
            PipelineMasterStage(self, "web_frontend", env=us_east_1)
        )


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
