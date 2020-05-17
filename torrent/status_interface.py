import tqdm
import asyncio
import sys
from math import ceil

MEGA = 1048576


async def run_tqdm(total_size, block_size, status_func):
    """
    for i in tqdm.trange(size, file=sys.stdout, leave=False, unit_scale=True):
        await q.get()
    """
    status = status_func()
    if status:
        print("The torrent is resuming progress reloading")
    pbar = tqdm.tqdm(unit='M', total= ceil(total_size / MEGA),
            file=sys.stdout, initial=(status * block_size / MEGA))
    while True:
        await asyncio.sleep(1)
        updated_status = status_func()
        if status < updated_status:
            block_to_update = updated_status - status
            pbar.update((block_to_update * block_size / MEGA))
            status = updated_status
