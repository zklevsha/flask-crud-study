import os
import json
import aiofiles
import asyncio
from typing import List, Dict
from random import randrange


json_folder = '/tmp'


async def async_read(fpath: str) -> List[Dict[str, str]]:
    """reader coroutine"""

    # simulating exeption
    if randrange(10) % 2 == 0:
        raise Exception

    # simulating long run
    await asyncio.sleep(randrange(3))

    # async reading
    async with aiofiles.open(fpath, mode='r') as f:
        contents = await f.read()
    return json.loads(contents)


async def async_read_with_timeout(fpath: str, timeout: float = 2):
    """timeout wrapper"""
    return await asyncio.wait_for(async_read(fpath), timeout=timeout)


def create_files():
    """
    creating json files that will be used as datasource
    """
    j1 = [{'id': i, 'name': f'Test {i}'} for i in range(1, 11)] + \
        [{'id': i, 'name': f'Test {i}'} for i in range(31, 41)]
    j2 = [{'id': i, 'name': f'Test {i}'} for i in range(11, 21)] + \
        [{'id': i, 'name': f'Test {i}'} for i in range(41, 51)]
    j3 = [{'id': i, 'name': f'Test {i}'} for i in range(21, 31)] + \
        [{'id': i, 'name': f'Test {i}'} for i in range(51, 61)]

    for j, fname in ((j1, 'j1.json'), (j2, 'j2.json'), (j3, 'j3.json')):
        with open(os.path.join(json_folder, fname), 'w') as f:
            json.dump(j, f)


async def async_read_files():
    fpaths = [os.path.join(json_folder, i)
              for i in ('j1.json', 'j2.json', 'j3.json')]
    tasks = [asyncio.create_task(async_read_with_timeout(f))
             for f in fpaths]
    return await asyncio.gather(*tasks, return_exceptions=True)
