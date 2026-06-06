from __future__ import annotations

import secrets
from typing import Dict


class AuthService:
    def __init__(self) -> None:
        self.users: Dict[str, str] = {}
        self.tokens: Dict[str, str] = {}

    def register(self, username: str, password: str) -> dict:
        if username in self.users:
            raise ValueError("username already exists")

        self.users[username] = password
        return {"username": username, "status": "registered"}

    def authenticate(self, username: str, password: str) -> str:
        if self.users.get(username) != password:
            raise ValueError("invalid credentials")

        token = secrets.token_urlsafe(32)
        self.tokens[token] = username
        return token

    def validate_token(self, token: str) -> str:
        username = self.tokens.get(token)
        if not username:
            raise ValueError("invalid token")
        return username

    def logout(self, token: str) -> dict:
        if token in self.tokens:
            self.tokens.pop(token)
            return {"status": "logged_out"}

        raise ValueError("invalid token")


auth_service = AuthService()
