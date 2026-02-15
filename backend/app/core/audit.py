"""Append-only audit log for security-sensitive actions.

Logs to a dedicated structured logger so audit events can be routed
to a separate sink (file, database, or log aggregation service).
"""

from datetime import datetime, timezone

from app.core.logging import get_logger

audit_logger = get_logger("audit")


def log_event(
    action: str,
    *,
    user_id: str | None = None,
    ip: str | None = None,
    request_id: str | None = None,
    resource: str | None = None,
    detail: str | None = None,
) -> None:
    """Record an audit event.

    Actions:
        auth.login, auth.logout, auth.magic_link_created,
        recommendation.created, recommendation.refined,
        group.created, group.joined,
        user.preferences_updated, user.watchlist_modified,
        admin.rate_limit_exceeded
    """
    audit_logger.info(
        "audit_event",
        action=action,
        user_id=user_id,
        ip=ip,
        request_id=request_id,
        resource=resource,
        detail=detail,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
