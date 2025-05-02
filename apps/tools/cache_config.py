from typing import Optional


class CacheConfig:
    use_cache: bool
    ttl: int
    invalidates: list[str]

    def __init__(
        self,
        key: str,
        use_cache: bool = False,
        ttl: int = 60,
        invalidates: Optional[list[str]] = None,
    ):
        if invalidates is None:
            invalidates = []

        self.use_cache = use_cache
        self.ttl = ttl
        self.invalidates = invalidates
        self.key = key
