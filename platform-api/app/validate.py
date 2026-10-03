import re

NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]{1,30}$")
ALLOWED_RUNTIMES = {"python"}
SELF_SERVE_ENVIRONMENTS = {"dev", "staging"}


def _name_ok(value: str) -> bool:
    return bool(NAME_PATTERN.match(value)) and not value.endswith("-")


def refusals_for(payload: dict) -> list[str]:
    refusals = []
    name = str(payload.get("name") or "").strip()
    team = str(payload.get("team") or "").strip()
    runtime = str(payload.get("runtime") or "").strip().lower()
    environment = str(payload.get("environment") or "").strip().lower()
    port = payload.get("port", 8080)

    if not _name_ok(name):
        refusals.append(
            "name must be 2-31 characters, start with a letter, and use only lowercase letters, numbers, and hyphens"
        )
    if not _name_ok(team):
        refusals.append("team is required and uses the same shape as the service name")
    if runtime not in ALLOWED_RUNTIMES:
        refusals.append("runtime python is the first template; other runtimes are not rendered")
    if environment == "prod" or environment == "production":
        refusals.append(
            "prod is not self-serve; open a pull request on the GitOps repository"
        )
    elif environment not in SELF_SERVE_ENVIRONMENTS:
        refusals.append("environment must be dev or staging")
    try:
        port_number = int(port)
    except (TypeError, ValueError):
        port_number = 0
    if not 1024 <= port_number <= 65535:
        refusals.append("port must be between 1024 and 65535")
    return refusals
