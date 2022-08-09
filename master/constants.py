import os

# General Constants
APP_NAME: str = "quakeservices"
DEFAULT_REGION: str = "us-west-2"
DEPLOYMENT_ENVIRONMENT: str = os.getenv("DEPLOYMENT_ENVIRONMENT", "prod")

# Master Constants
DEFAULT_MASTER_PORT: int = 27900

# Client Constants
DEFAULT_HOST_ADDRESS: str = "master.quake.services"
DEFAULT_HOST_PORT: int = DEFAULT_MASTER_PORT
DEFAULT_CLIENT_ADDRESS: str = "0.0.0.0"
DEFAULT_CLIENT_PORT: int = 27910
DEFAULT_TIMEOUT: float = 30.0
DEFAULT_BUFFER: int = 1024
