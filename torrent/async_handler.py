import asyncio
import logging


logger = logging.getLogger(__name__)


def get_loop():
    return asyncio.get_event_loop() 


def run_async_task(loop, func):
    return loop.create_task(func)
