import asyncio
import logging


logger = logging.getLogger(__name__)


def get_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


def run_async_task(loop, func):
    return loop.create_task(func)
