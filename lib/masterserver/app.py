#!/usr/bin/env python
import logging
import os
import sys

from masterserver import MasterServer
from transport import Transport


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


def main() -> None:
    master = MasterServer()
    transport = Transport(master)

    try:
        transport.loop.run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    os.environ["STAGE"] = os.getenv("STAGE", "PRODUCTION")

    if os.getenv("STAGE") == "TESTING":
        setup_logging("DEBUG")
    else:
        setup_logging("DEBUG")

    logging.info("Starting master server.")
    main()
    logging.info("Master server stopped.")
