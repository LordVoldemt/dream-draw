from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class SessionToken:
    token: str
    user_id: int
    expires_at: datetime


class SessionManager:
    def __init__(self) -> None:
        self._tokens: dict[str, SessionToken] = {}

    def issue_user_token(self, user_id: int, ttl_hours: int = 24) -> str:
        token = secrets.token_urlsafe(24)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
        self._tokens[token] = SessionToken(token=token, user_id=user_id, expires_at=expires_at)
        return token

    def get_user_id(self, token: str) -> int | None:
        session = self._tokens.get(token)
        if session is None:
            return None
        if session.expires_at <= datetime.now(timezone.utc):
            self._tokens.pop(token, None)
            return None
        return session.user_id


session_manager = SessionManager()
admin_session_manager = SessionManager()
