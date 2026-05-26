import asyncio
import logging
import signal

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import booking as db
import sheets
from handlers import router
from settings import BOT_TOKEN, HEALTH_PORT, REDIS_URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _make_storage():
    if REDIS_URL:
        from aiogram.fsm.storage.redis import RedisStorage

        logger.info("Using Redis FSM storage")
        return RedisStorage.from_url(REDIS_URL)
    logger.info("Using in-memory FSM storage (state is lost on restart)")
    return MemoryStorage()


async def _health_handler(_request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


async def run_health_server(stop: asyncio.Event) -> None:
    app = web.Application()
    app.router.add_get("/", _health_handler)
    app.router.add_get("/health", _health_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", HEALTH_PORT)
    await site.start()
    logger.info("Health check server listening on 0.0.0.0:%s", HEALTH_PORT)

    await stop.wait()
    await runner.cleanup()


async def main() -> None:
    db.init_db()
    sheets.ensure_headers()

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher(storage=_make_storage())
    dp.include_router(router)

    stop = asyncio.Event()

    def _request_shutdown() -> None:
        logger.info("Shutdown requested")
        stop.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _request_shutdown)

    await bot.delete_webhook(drop_pending_updates=True)

    health_task = asyncio.create_task(run_health_server(stop))
    try:
        await dp.start_polling(bot, handle_signals=False)
    finally:
        stop.set()
        await health_task
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
