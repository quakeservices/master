#!/usr/bin/env python
import logging
import os
import sys

from master import MasterServer


def setup_logging(level: str = "INFO"):
    # logging.getLogger('boto3').propagate = False
    # logging.getLogger('botocore').propagate = False

    log_level = getattr(logging, level.upper())

    logging.basicConfig(
        stream=sys.stdout,
        level=log_level,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def setup_environment():
    os.environ["DEPLOYMENT_ENVIRONMENT"] = os.getenv(
        "DEPLOYMENT_ENVIRONMENT", "development"
    )

    if os.getenv("DEPLOYMENT_ENVIRONMENT") == "production":
        setup_logging("INFO")
    else:
        setup_logging("DEBUG")


def main():
    logging.info("Starting master server.")

    masterserver = MasterServer()

    masterserver.start()

    logging.info("Master server stopped.")


if __name__ == "__main__":
    setup_environment()
    main()
