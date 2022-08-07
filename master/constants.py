import os

APP_NAME: str = "quakeservices"
DEFAULT_REGION: str = "us-west-2"
DEPLOYMENT_ENVIRONMENT: str = os.getenv("DEPLOYMENT_ENVIRONMENT", "prod")
