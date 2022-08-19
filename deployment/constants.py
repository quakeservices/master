import os

from deployment.types import Records

APP_NAME: str = "quakeservices"
DOMAIN_NAME: str = "quake.services"
REPO: str = f"{APP_NAME}/master"
DEPLOYMENT_ENVIRONMENT: str = os.getenv("DEPLOYMENT_ENVIRONMENT", "prod")

DOMAINS: list[str] = [DOMAIN_NAME, "quake2.services", "quake3.services"]
RECORDS: Records = {
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
