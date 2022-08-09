import logging

from master.server.servers.master import MasterServer


def _run() -> None:
    logging.info("Starting master server.")

    masterserver = MasterServer()
    masterserver.initialise()
    masterserver.start()

    logging.info("Master server stopped.")
