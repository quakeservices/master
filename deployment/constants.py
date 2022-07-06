APP_NAME: str = "quakeservices"
DOMAIN_NAME: str = "quake.services"
REPO: str = f"{APP_NAME}/master"

DOMAINS: list[str] = [DOMAIN_NAME, "quake2.services", "quake3.services"]

RECORDS: dict[str, list[dict[str, str]]] = {
    "quake.services": [
        {
            "type": "TXT",
            "key": "_github-pages-challenge-quakeservices",
            "value": "4cbb312cf881980e8b6ddef434f26bu",
        }
    ]
}
