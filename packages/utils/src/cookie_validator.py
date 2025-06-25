class CookieValidator:
    """Simple helper validating expected cookie fields."""
    REQUIRED_FIELDS = {"domain", "name", "value", "path", "expires"}

    @classmethod
    def validate(cls, cookies):
        """Validate a cookie dict or list of dicts."""
        if isinstance(cookies, dict):
            cookies = [cookies]
        for idx, cookie in enumerate(cookies):
            missing = cls.REQUIRED_FIELDS - cookie.keys()
            if missing:
                raise ValueError(f"Cookie {idx} missing fields: {sorted(missing)}")
        return True
