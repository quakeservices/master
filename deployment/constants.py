import os
from typing import Union

APP_NAME: str = "quakeservices"
DOMAIN_NAME: str = "quake.services"
REPO: str = f"{APP_NAME}/master"
DEPLOYMENT_ENVIRONMENT: str = os.getenv("DEPLOYMENT_ENVIRONMENT", "prod")

DOMAINS: list[str] = [DOMAIN_NAME, "quake2.services", "quake3.services"]

RECORDS: dict[str, list[dict[str, Union[str, list[str]]]]] = {
    "quake.services": [
        {
            "type": "TXT",
            "key": "_github-pages-challenge-quakeservices",
            "values": [
                "4cbb312cf881980e8b6ddef434f26b",  # Quake Services Organisation
                "4cbb312cf881980e8b6ddef434f26bu",  # Quake Services Master
            ],
        },
        {
            "type": "CNAME",
            "key": "docs",
            "value": "quakeservices.github.io",
        },
    ]
}
