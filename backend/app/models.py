from __future__ import annotations

from pydantic import BaseModel


class AuthPayload(BaseModel):
    username: str
    password: str


class AdviceRequestPayload(BaseModel):
    lat: float
    lon: float
    farmer_phone: str | None = None


class SubscribePayload(BaseModel):
    lat: float
    lon: float
    phone: str


class UnsubscribePayload(BaseModel):
    phone: str
