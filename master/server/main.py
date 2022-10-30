import logging

from master.constants import DEPLOYMENT_ENVIRONMENT
from master.server.servers.master import MasterServer


def _run() -> None:
    logging.info("Starting master server...")
    logging.info("DEPLOYMENT_ENVIRONMENT is set to %s", DEPLOYMENT_ENVIRONMENT)

    masterserver = MasterServer()
    masterserver.initialise(storage_backend="dynamodb")
    masterserver.start()

    logging.info("Master server stopped.")
