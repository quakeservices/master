import os

from aws_cdk import Environment

__all__ = ["us_west_2", "us_east_1"]

default_account: str = os.getenv(
    "AWS_ACCOUNT", os.getenv("CDK_DEFAULT_ACCOUNT", "123456789012")
)
default_region: str = "us-west-2"
us_west_2 = Environment(account=default_account, region=default_region)
us_east_1 = Environment(account=default_account, region="us-east-1")
