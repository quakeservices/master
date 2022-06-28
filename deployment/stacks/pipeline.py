from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as codepipeline_actions
from aws_cdk import aws_ssm as ssm
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from constructs import Construct

from deployment.constants import APP_NAME, REPO
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
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.pipeline = self._create_pipeline()
        self._create_infra_stage()

    def _create_pipeline(self):

        return CodePipeline(
            self,
            "pipeline",
            pipeline_name=APP_NAME,
            synth=ShellStep(
                "Synth",
                input=CodePipelineSource.connection(
                    REPO, "main", connection_arn=connection_arn
                ),
                commands=[
                    "npm install -g aws-cdk",
                    "python -m pip install -r deployment/requirements.txt",
                    "cdk synth --app ./app.py",
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


class TestPipelineStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        connection_arn = ssm.StringParameter.from_string_parameter_attributes(
            self,
            "connection-arn",
            parameter_name="/quakeservices/codepipeline/connection-arn",
        ).string_value
        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            action_name="GitHub Source",
            owner=APP_NAME,
            repo="master",
            branch="main",
            output=source_output,
            connection_arn=connection_arn,
        )

        test_action = codepipeline_actions.CodeBuildAction(
            action_name="Test CDK Action",
            input=source_output,
            project=codebuild.PipelineProject(
                self,
                "Test CDK Project",
                build_spec=codebuild.BuildSpec.from_object(
                    {
                        "version": "0.2",
                        "phases": {
                            "install": {
                                "commands": [
                                    "pip install -r deployment/requirements.txt",
                                    "pip install -r tests/requirements.txt",
                                ]
                            },
                            "build": {"commands": "pytest -v test/cdk"},
                        },
                    }
                ),
            ),
            variables_namespace="MyNamespace",
        )

        pipeline = codepipeline.Pipeline(
            self,
            "MyFirstPipeline",
            pipeline_name="MyPipeline",
            cross_account_keys=False,
            stages=[codepipeline.StageProps(stage_name="Source", actions=[])],
        )
