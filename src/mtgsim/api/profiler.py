"""SQL query profiler using SQLAlchemy engine events.

Tracks per-request query count, timing, and SQL statements via contextvars.
Attach to an engine with `attach_profiler(engine)`, then use the middleware
or call `start_profiling()` / `get_profile()` manually.
"""

import logging
import time
from collections import deque
from contextvars import ContextVar
from dataclasses import dataclass, field

from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger("mtgsim.api.profiler")

# Per-request state stored in contextvars so concurrent requests don't collide
_request_queries: ContextVar[list | None] = ContextVar("_request_queries", default=None)
_query_start_time: ContextVar[float | None] = ContextVar("_query_start_time", default=None)

# Ring buffer of recent request profiles for the debug endpoint
MAX_HISTORY = 200
_profile_history: deque["RequestProfile"] = deque(maxlen=MAX_HISTORY)


@dataclass
class QueryRecord:
    sql: str
    params_repr: str
    duration_ms: float


@dataclass
class RequestProfile:
    method: str
    path: str
    query_string: str
    query_count: int
    total_query_ms: float
    request_ms: float
    queries: list[QueryRecord] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


def attach_profiler(engine: Engine) -> None:
    """Register before/after cursor execute events on the engine."""

    @event.listens_for(engine, "before_cursor_execute")
    def _before(conn, cursor, statement, parameters, context, executemany):
        queries = _request_queries.get()
        if queries is not None:
            _query_start_time.set(time.perf_counter())

    @event.listens_for(engine, "after_cursor_execute")
    def _after(conn, cursor, statement, parameters, context, executemany):
        queries = _request_queries.get()
        start = _query_start_time.get()
        if queries is not None and start is not None:
            duration_ms = (time.perf_counter() - start) * 1000
            params_str = repr(parameters)[:200] if parameters else ""
            queries.append(QueryRecord(sql=statement, params_repr=params_str, duration_ms=duration_ms))
            _query_start_time.set(None)


def start_profiling() -> None:
    """Begin collecting queries for the current context."""
    _request_queries.set([])


def stop_profiling() -> list[QueryRecord]:
    """Stop collecting and return the recorded queries."""
    queries = _request_queries.get() or []
    _request_queries.set(None)
    return queries


def record_profile(profile: RequestProfile) -> None:
    """Store a completed profile in the history ring buffer."""
    _profile_history.append(profile)
    if profile.total_query_ms > 100 or profile.query_count > 5:
        logger.info(
            f"PROFILE {profile.method} {profile.path}{profile.query_string} "
            f"queries={profile.query_count} db={profile.total_query_ms:.1f}ms "
            f"total={profile.request_ms:.1f}ms"
        )


def get_history(
    min_queries: int = 0,
    min_db_ms: float = 0,
    path_contains: str = "",
    limit: int = 50,
) -> list[RequestProfile]:
    """Return recent profiles matching the filters, newest first."""
    results = []
    for p in reversed(_profile_history):
        if p.query_count < min_queries:
            continue
        if p.total_query_ms < min_db_ms:
            continue
        if path_contains and path_contains not in p.path:
            continue
        results.append(p)
        if len(results) >= limit:
            break
    return results
