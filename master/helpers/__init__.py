import logging
import os
import sys


def setup_logging(
    log_level: str, hide_boto_logs: bool, show_time: bool = False
) -> None:
    if hide_boto_logs:
        logging.getLogger("boto3").propagate = False
        logging.getLogger("botocore").propagate = False

    if show_time:
        format = "%(asctime)s %(levelname)s %(message)s"
    else:
        format = "%(levelname)s %(message)s"

    logging.basicConfig(
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
        format=format,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.info(f"Logging set to {log_level.upper()}")


def setup_environment() -> None:
    if not os.getenv("DEPLOYMENT_ENVIRONMENT", None):
        os.environ["DEPLOYMENT_ENVIRONMENT"] = "dev"
        logging.info("DEPLOYMENT_ENVIRONMENT unset. Setting to 'dev'")
