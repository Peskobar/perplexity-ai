from typing import Iterable, Mapping

REQUIRED_FIELDS = {"domain", "name", "value", "path", "expires"}


def validate_emailnator_cookies(cookies: Iterable[Mapping]) -> None:
    """Validate Emailnator cookies contain required fields."""
    for idx, ck in enumerate(cookies):
        missing = REQUIRED_FIELDS - set(ck.keys())
        if missing:
            raise ValueError(f"Cookie {idx} missing fields: {', '.join(sorted(missing))}")

