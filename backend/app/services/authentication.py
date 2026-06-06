from __future__ import annotations

import secrets

from sqlalchemy import select

from app.database import Token, User, async_session


class AuthService:
    async def register(self, username: str, password: str) -> dict:
        async with async_session() as session:
            result = await session.execute(select(User).where(User.username == username))
            if result.scalar_one_or_none():
                raise ValueError("username already exists")

            session.add(User(username=username, password=password))
            await session.commit()
            return {"username": username, "status": "registered"}

    async def authenticate(self, username: str, password: str) -> str:
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
        async with async_session() as session:
            result = await session.execute(select(Token).where(Token.token == token))
            t = result.scalar_one_or_none()
            if not t:
                raise ValueError("invalid token")
            return t.username

    async def logout(self, token: str) -> dict:
        async with async_session() as session:
            result = await session.execute(select(Token).where(Token.token == token))
            t = result.scalar_one_or_none()
            if not t:
                raise ValueError("invalid token")

            await session.delete(t)
            await session.commit()
            return {"status": "logged_out"}


auth_service = AuthService()
