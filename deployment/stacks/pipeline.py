from typing import Any

from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from aws_cdk.aws_codebuild import BuildEnvironment
from aws_cdk.pipelines import CodeBuildStep, CodePipeline, CodePipelineSource, ShellStep
from constructs import Construct

from deployment.constants import APP_NAME, DEPLOYMENT_ENVIRONMENT, REPO
from deployment.environments import us_east_1, us_west_2
from deployment.stacks.pipelines import PipelineInfraStage, PipelineMasterStage


class PipelineStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.pipeline_source = self._pipeline_source
        self.connection = self._pipeline_connection
        self.pipeline = self._create_pipeline()
        self._create_infra_stage()
        self._create_master_stage()

    def _create_pipeline(self) -> CodePipeline:
        # test_step = self._create_pipeline_test_step()
        build_step = self._create_pipeline_build_step()
        # build_step.add_step_dependency(test_step)

        return CodePipeline(
            self,
            "pipeline",
            pipeline_name=APP_NAME,
            docker_enabled_for_synth=True,
            docker_enabled_for_self_mutation=True,
            synth=build_step,
        )

    @property
    def _pipeline_source(self) -> str:
        return ssm.StringParameter.from_string_parameter_attributes(
            self,
            "connection-arn",
            parameter_name="/quakeservices/codepipeline/connection-arn",
        ).string_value

    @property
    def _pipeline_connection(self) -> CodePipelineSource:
        return CodePipelineSource.connection(
            REPO, "main", connection_arn=self.pipeline_source
        )

    def _create_pipeline_build_step(self) -> CodeBuildStep:
        commands: list[str] = [
            "npm install --global aws-cdk",
            "poetry install --with cdk",
            "cdk synth",
        ]
        return CodeBuildStep(
            f"{APP_NAME}-synth",
            project_name=f"{APP_NAME}-synth",
            input=self.connection,
            commands=commands,
            env={"DOCKER_BUILDKIT": "1", "POETRY_VIRTUALENVS_CREATE": "false"},
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
        )

    def _create_pipeline_test_step(self) -> ShellStep:
        commands: list[str] = [
            "npm install --global aws-cdk",
            "poetry install --with cdk",
            "pytest -v test/unit/cdk",
        ]
        return ShellStep(
            "Test",
            input=self.connection,
            commands=commands,
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
