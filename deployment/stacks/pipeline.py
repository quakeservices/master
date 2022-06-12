from aws_cdk import RemovalPolicy, Stack
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from constructs import Construct
from deployment.constants import APP_NAME, REPO
from deployment.environments import us_east_1, us_west_2
from deployment.stacks.pipelines import (PipelineInfraStage,
                                         PipelineMasterStage,
                                         PipelineWebBackendStage,
                                         PipelineWebFrontendStage)


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
        self.pipeline.add_stage(
            PipelineWebBackendStage(self, "web_backend", env=us_west_2)
        )

    def _create_web_frontend_stage(self):
        self.pipeline.add_stage(
            PipelineWebFrontendStage(self, "web_frontend", env=us_east_1)
        )
