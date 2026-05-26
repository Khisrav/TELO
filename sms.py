import logging

import aiohttp
from aiogram import Bot

from keyboards import approve_kb
from settings import SMSRU_API, SPECIALIST_PHONE, SPECIALIST_TG_ID

logger = logging.getLogger(__name__)


async def send_sms(text: str):
    if not SMSRU_API:
        return
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(
                "https://sms.ru/sms/send",
                data={
                    "api_id": SMSRU_API,
                    "to": SPECIALIST_PHONE,
                    "msg": text[:700],
                    "json": 1,
                },
            )
    except Exception:
        logger.exception("Failed to send SMS")


async def notify_specialist(bot: Bot, booking: dict):
    text = (
        f"🔔 Новая заявка #{booking['id']}\n"
        f"👤 {booking['full_name']} (@{booking['username']})\n"
        f"📞 {booking['phone']}\n"
        f"💆 {booking['category']} → {booking['service']}\n"
        f"💰 {booking['price']} ₽ ({booking['duration']})\n"
        f"📅 {booking['date']} в {booking['time']}"
    )

    await send_sms(text)

    try:
        await bot.send_message(
            SPECIALIST_TG_ID,
            text,
            reply_markup=approve_kb(booking["id"]),
        )
    except Exception:
        logger.exception("Failed to notify specialist in Telegram")
