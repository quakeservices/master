from typing import Callable

import pytest
from aws_cdk import App, Environment, Stack
from aws_cdk import aws_route53 as route53


@pytest.fixture(scope="class")
def stack_app() -> App:
    return App()


@pytest.fixture(scope="session")
def stack_env_us_west_2() -> Environment:
    return Environment(
        account="123456789012",
        region="us-west-2",
    )


@pytest.fixture(scope="session")
def stack_env_us_east_1() -> Environment:
    return Environment(
        account="123456789012",
        region="us-east-1",
    )


@pytest.fixture()
def stack(stack_app: App, stack_env_us_west_2: Environment) -> Stack:
    return Stack(stack_app, "TestStack", env=stack_env_us_west_2)


@pytest.fixture()
def zone() -> Callable:
    def _create_zone(
        local_stack: Stack, domain: str = "example.com"
    ) -> route53.IHostedZone:
        return route53.PublicHostedZone(local_stack, f"test{domain}", zone_name=domain)

    return _create_zone
