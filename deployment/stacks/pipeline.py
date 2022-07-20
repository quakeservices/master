from typing import Any

from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from aws_cdk.pipelines import CodeBuildStep, CodePipeline, CodePipelineSource
from constructs import Construct

from deployment.constants import APP_NAME, DEPLOYMENT_ENVIRONMENT, REPO
from deployment.environments import us_east_1, us_west_2
from deployment.stacks.pipelines import (
    PipelineInfraStage,
    PipelineMasterStage,
    PipelineWebBackendStage,
    PipelineWebFrontendStage,
)


class PipelineStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.pipeline = self._create_pipeline()
        self._create_infra_stage()
        self._create_master_stage()

    def _create_pipeline(self) -> CodePipeline:
        connection_arn = ssm.StringParameter.from_string_parameter_attributes(
            self,
            "connection-arn",
            parameter_name="/quakeservices/codepipeline/connection-arn",
        ).string_value

        commands: list[str] = [
            "npm install --global aws-cdk",
            "pip install -r deployment/requirements.txt",
            "cdk synth",
        ]

        return CodePipeline(
            self,
            "pipeline",
            pipeline_name=APP_NAME,
            docker_enabled_for_synth=True,
            synth=CodeBuildStep(
                f"{APP_NAME}-synth",
                project_name=f"{APP_NAME}-synth",
                input=CodePipelineSource.connection(
                    REPO, "main", connection_arn=connection_arn
                ),
                commands=commands,
                role_policy_statements=[
                    iam.PolicyStatement(
                        actions=["sts:AssumeRole"],
                        resources=["*"],
                        conditions={
                            "StringEquals": {
                                "iam:ResourceTag/aws-cdk:bootstrap-role": "lookup"
                            }
                        },
                    )
                ],
            ),
        )

    def _create_infra_stage(self) -> None:
        self.pipeline.add_stage(
            PipelineInfraStage(
                self,
                f"{APP_NAME}-infra",
                deployment_environment=DEPLOYMENT_ENVIRONMENT,
                env=us_west_2,
            )
        )

    def _create_master_stage(self) -> None:
        self.pipeline.add_stage(
            PipelineMasterStage(
                self,
                f"{APP_NAME}-master",
                deployment_environment=DEPLOYMENT_ENVIRONMENT,
                env=us_west_2,
            )
        )
