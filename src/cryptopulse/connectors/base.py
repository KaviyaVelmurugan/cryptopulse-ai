"""Shared connector types and a small retrying JSON HTTP client."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Callable, Generic, Protocol, TypeVar
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


T = TypeVar("T")


class ConnectorError(RuntimeError):
    """A safe connector failure that can be shown to an operator."""


class AuthenticationError(ConnectorError):
    """The provider rejected or did not receive the required credential."""


class RateLimitError(ConnectorError):
    """The provider rate limit remained active after retries."""


class ProviderResponseError(ConnectorError):
    """The provider returned invalid or unexpected data."""


class JsonTransport(Protocol):
    def get_json(
        self,
        url: str,
        *,
        params: dict[str, str | int],
        headers: dict[str, str],
    ) -> object: ...


@dataclass(frozen=True, slots=True)
class FetchResult(Generic[T]):
    records: tuple[T, ...]
    warnings: tuple[str, ...] = ()


class UrllibJsonTransport:
    """Dependency-free HTTP transport with bounded exponential retry."""

    def __init__(
        self,
        *,
        timeout_seconds: float = 15.0,
        max_attempts: int = 3,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts
        self.sleep = sleep

    def get_json(
        self,
        url: str,
        *,
        params: dict[str, str | int],
        headers: dict[str, str],
    ) -> object:
        query = urlencode(params)
        request = Request(
            f"{url}?{query}" if query else url,
            headers={"Accept": "application/json", "User-Agent": "CryptoPulseAI/0.1", **headers},
        )
        last_error: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                if exc.code in {401, 403}:
                    raise AuthenticationError(f"provider authentication failed with HTTP {exc.code}") from exc
                if exc.code == 429:
                    last_error = exc
                elif 500 <= exc.code < 600:
                    last_error = exc
                else:
                    raise ConnectorError(f"provider request failed with HTTP {exc.code}") from exc
            except (URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
            if attempt < self.max_attempts:
                self.sleep(float(2 ** (attempt - 1)))
        if isinstance(last_error, HTTPError) and last_error.code == 429:
            raise RateLimitError("provider rate limit remained active after retries") from last_error
        raise ConnectorError("provider request failed after retries") from last_error
