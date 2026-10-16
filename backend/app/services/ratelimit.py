"""Kayan pencereli basit hız sınırlayıcı.

Süreç içi bellekte tutulur; tek süreçli dağıtım için yeterlidir. Birden fazla
worker/instance ile çalışılacaksa Redis tabanlı bir sınırlayıcıyla değiştirilmelidir.
"""

import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, status


class RateLimiter:
    def __init__(self, limit: int, window_seconds: float) -> None:
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, record: bool = True) -> None:
        """Sınır aşıldıysa 429 fırlatır. record=False ise yalnızca kontrol eder, saymaz."""
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] > self.window:
                hits.popleft()
            if len(hits) >= self.limit:
                raise HTTPException(
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    "Çok fazla deneme yapıldı. Lütfen biraz sonra tekrar deneyin.",
                    headers={"Retry-After": str(int(self.window))},
                )
            if record:
                hits.append(now)

    def hit(self, key: str) -> None:
        with self._lock:
            self._hits[key].append(time.monotonic())

    def clear(self, key: str) -> None:
        with self._lock:
            self._hits.pop(key, None)

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


login_limiter = RateLimiter(limit=10, window_seconds=15 * 60)
assistant_limiter = RateLimiter(limit=20, window_seconds=60)
