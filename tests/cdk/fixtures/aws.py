import pytest
from aws_cdk import App, Environment


@pytest.fixture(scope="class")
def stack_app():
    return App()


@pytest.fixture(scope="session")
def stack_env_us_west_2():
    return Environment(
        account="123456789012",
        region="us-west-2",
    )


@pytest.fixture(scope="session")
def stack_env_us_east_1():
    return Environment(
        account="123456789012",
        region="us-east-1",
    )
