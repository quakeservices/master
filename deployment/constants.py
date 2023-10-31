import os
from typing import Final

from deployment.types import Records

__all__ = [
    "APP_NAME",
    "DOMAIN_NAME",
    "REPO",
    "DEPLOYMENT_ENVIRONMENT",
    "MASTER_PORT",
    "MASTER_HEALTHCHECK_PORT",
    "MASTER_CPU",
    "MASTER_MEMORY",
    "DEFAULT_TIMEOUT",
    "DOMAINS",
    "RECORDS",
]


APP_NAME: Final[str] = "quakeservices"
DOMAIN_NAME: Final[str] = "quake.services"
REPO: Final[str] = f"{APP_NAME}/master"
DEPLOYMENT_ENVIRONMENT: Final[str] = os.getenv("DEPLOYMENT_ENVIRONMENT", "prod")

MASTER_PORT: Final[int] = 27900
MASTER_HEALTHCHECK_PORT: Final[int] = 8080
MASTER_CPU: Final[int] = 512
MASTER_MEMORY: Final[int] = 1024
DEFAULT_TIMEOUT: Final[int] = 15

DOMAINS: Final[list[str]] = [DOMAIN_NAME, "quake2.services", "quake3.services"]
RECORDS: Final[Records] = {
    "quake.services": {
        "TXT": [
            {
                "key": "_github-pages-challenge-quakeservices",
                "values": [
                    "4cbb312cf881980e8b6ddef434f26b",  # Quake Services Organisation
                    "4cbb312cf881980e8b6ddef434f26bu",  # Quake Services Master
                ],
            }
        ],
        "CNAME": [
            {
                "key": "docs",
                "values": ["quakeservices.github.io"],
            }
        ],
        "A": [
            {
                "key": "mel",
                "values": "45.121.209.140",
            }
        ],
    }
}
