from __future__ import annotations

import logging
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from app.config import settings
from app.database import Subscriber, async_session
from app.services.africastalking import africastalking_service
from app.services.crop_advice import crop_advice_service
from app.services.harvest_reminder import harvest_reminder_service
from app.services.pest_disease import pest_disease_service
from app.services.weather import weather_service

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self) -> None:
        self._scheduler: AsyncIOScheduler | None = None

    async def get_subscribers(self) -> list[dict[str, Any]]:
        async with async_session() as session:
            result = await session.execute(select(Subscriber))
            return [
                {"lat": s.lat, "lon": s.lon, "phone": s.phone}
                for s in result.scalars().all()
            ]

    async def add_subscriber(self, lat: float, lon: float, phone: str) -> dict:
        async with async_session() as session:
            result = await session.execute(
                select(Subscriber).where(Subscriber.phone == phone)
            )
            existing = result.scalar_one_or_none()
            if existing:
                existing.lat = lat
                existing.lon = lon
                await session.commit()
                return {"phone": phone, "lat": lat, "lon": lon, "status": "updated"}

            session.add(Subscriber(phone=phone, lat=lat, lon=lon))
            await session.commit()
            return {"phone": phone, "lat": lat, "lon": lon, "status": "subscribed"}

    async def remove_subscriber(self, phone: str) -> dict:
        async with async_session() as session:
            result = await session.execute(
                select(Subscriber).where(Subscriber.phone == phone)
            )
            sub = result.scalar_one_or_none()
            if not sub:
                return {"phone": phone, "status": "not_found"}

            await session.delete(sub)
            await session.commit()
            return {"phone": phone, "status": "unsubscribed"}

    async def _seed_default(self) -> None:
        phone = settings.farmer_phone
        if not phone:
            return

        async with async_session() as session:
            result = await session.execute(
                select(Subscriber).where(Subscriber.phone == phone)
            )
            if not result.scalar_one_or_none():
                session.add(
                    Subscriber(phone=phone, lat=settings.farmer_lat, lon=settings.farmer_lon)
                )
                await session.commit()
                logger.info("Seeded default subscriber: %s", phone)

    async def _deliver_to_subscriber(self, sub: dict[str, Any]) -> dict[str, Any] | None:
        lat = sub["lat"]
        lon = sub["lon"]
        phone = sub["phone"]

        try:
            weather = await weather_service.get_current(lat, lon)
        except Exception as e:
            logger.error("Weather fetch failed for %s: %s", phone, e)
            return None

        try:
            crop_advice = crop_advice_service.suggest(weather)
        except Exception as e:
            logger.error("Crop advice failed for %s: %s", phone, e)
            crop_advice = ""

        try:
            pest_alert = pest_disease_service.suggest(weather)
        except Exception as e:
            logger.error("Pest/disease advice failed for %s: %s", phone, e)
            pest_alert = ""

        try:
            harvest_reminder = harvest_reminder_service.suggest(weather)
        except Exception as e:
            logger.error("Harvest reminder failed for %s: %s", phone, e)
            harvest_reminder = ""

        message_parts = [p for p in [crop_advice, pest_alert, harvest_reminder] if p]
        if not message_parts:
            logger.warning("No advice generated for %s", phone)
            return None

        message = "\n\n".join(message_parts)

        sms_status = "failed"
        try:
            africastalking_service.send_sms(message, to=phone)
            logger.info("Advice delivered to %s", phone)
            sms_status = "sent"
        except Exception as e:
            logger.error("SMS send failed for %s: %s", phone, e)

        return {
            "phone": phone,
            "crop_advice": crop_advice,
            "pest_alert": pest_alert,
            "harvest_reminder": harvest_reminder,
            "sms_status": sms_status,
        }

    async def deliver_all(self) -> dict[str, Any]:
        subscribers = await self.get_subscribers()

        if not subscribers:
            logger.info("No subscribers to deliver to")
            return {"delivered": 0, "total": 0, "results": []}

        results = []
        for sub in subscribers:
            result = await self._deliver_to_subscriber(sub)
            if result:
                results.append(result)

        return {
            "delivered": len(results),
            "total": len(subscribers),
            "results": results,
        }

    async def start(self) -> None:
        if self._scheduler and self._scheduler.running:
            logger.warning("Scheduler already running")
            return

        await self._seed_default()

        subscribers = await self.get_subscribers()
        if not subscribers:
            logger.info("No subscribers configured — scheduler will not start")
            return

        self._scheduler = AsyncIOScheduler()
        cron = settings.scheduler_cron
        parts = cron.strip().split()
        if len(parts) == 5:
            trigger = CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                day_of_week=parts[4],
            )
        else:
            logger.warning("Invalid cron expression '%s', using default 6 AM daily", cron)
            trigger = CronTrigger(hour=6, minute=0)

        self._scheduler.add_job(
            self.deliver_all,
            trigger=trigger,
            id="daily_advice_delivery",
            replace_existing=True,
        )
        self._scheduler.start()
        logger.info(
            "Scheduler started with cron: %s (%d subscriber(s))",
            cron,
            len(subscribers),
        )

    def stop(self) -> None:
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")


scheduler_service = SchedulerService()
