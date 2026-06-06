from __future__ import annotations

import re
import secrets

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import Token, User, async_session


class AuthService:
    async def register(self, username: str, password: str) -> dict:
        username = (username or "").strip()
        if not username:
            raise ValueError("username is required")
        if not password or not password.strip():
            raise ValueError("password is required")

        async with async_session() as session:
            try:
                session.add(User(username=username, password=password))
                await session.commit()
                return {"username": username, "status": "registered"}
            except IntegrityError:
                await session.rollback()
                raise ValueError("username already exists")

    async def authenticate(self, username: str, password: str) -> str:
        username = (username or "").strip()
        if not username:
            raise ValueError("username is required")
        if not password:
            raise ValueError("password is required")

        async with async_session() as session:
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()
            if not user or user.password != password:
                raise ValueError("invalid credentials")

            token = secrets.token_urlsafe(32)
            session.add(Token(token=token, username=username))
            await session.commit()
            return token

    async def validate_token(self, token: str) -> str:
        if not token:
            raise ValueError("invalid token")

        async with async_session() as session:
            result = await session.execute(select(Token).where(Token.token == token))
            t = result.scalar_one_or_none()
            if not t:
                raise ValueError("invalid token")
            return t.username

    async def logout(self, token: str) -> dict:
        if not token:
            raise ValueError("invalid token")

        async with async_session() as session:
            result = await session.execute(select(Token).where(Token.token == token))
            t = result.scalar_one_or_none()
            if not t:
                raise ValueError("invalid token")

            await session.delete(t)
            await session.commit()
            return {"status": "logged_out"}


auth_service = AuthService()
