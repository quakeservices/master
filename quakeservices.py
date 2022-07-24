#!/usr/bin/env python
import logging
import os
import sys

from master.server import MasterServer


def setup_logging(level: str = "INFO") -> None:
    # logging.getLogger('boto3').propagate = False
    # logging.getLogger('botocore').propagate = False

    log_level = getattr(logging, level.upper())

    logging.basicConfig(
        stream=sys.stdout,
        level=log_level,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.info(f"Logging set to {level.upper()}")


def setup_environment() -> None:
    os.environ["DEPLOYMENT_ENVIRONMENT"] = os.getenv(
        "DEPLOYMENT_ENVIRONMENT", "development"
    )

    if os.getenv("DEPLOYMENT_ENVIRONMENT") == "production":
        setup_logging("INFO")
    else:
        setup_logging("DEBUG")


def main() -> None:
    logging.info("Starting master server.")

    masterserver = MasterServer()
    masterserver.initialise()
    masterserver.start()

    logging.info("Master server stopped.")


if __name__ == "__main__":
    setup_environment()
    main()
