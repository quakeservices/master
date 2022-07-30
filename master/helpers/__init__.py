import logging
import os
import sys


def setup_logging(log_level: str, boto_logs: bool) -> None:
    if boto_logs:
        logging.getLogger("boto3").propagate = False
        logging.getLogger("botocore").propagate = False

    logging.basicConfig(
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.info(f"Logging set to {log_level.upper()}")


def setup_environment() -> None:
    if not os.getenv("DEPLOYMENT_ENVIRONMENT", None):
        os.environ["DEPLOYMENT_ENVIRONMENT"] = "development"
        logging.info("DEPLOYMENT_ENVIRONMENT unset. Setting to 'development'")
