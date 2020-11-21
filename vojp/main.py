import asyncio
import os
import logging
from vojp.gui import Gui
from datetime import datetime


async def main():
    setup_logger()
    # Show Gui
    gui = Gui()
    gui.start_gui()

    while True:
        await asyncio.sleep(50000)


async def shutdown():
    logging.info(msg='Shutting down asyncio event loop')
    loop = asyncio.get_running_loop()
    tasks = [task for task in asyncio.all_tasks() if task != asyncio.current_task()]
    [task.cancel() for task in tasks]
    done, pending = await asyncio.wait(await asyncio.gather(*tasks, return_exceptions=True))
    loop.stop()


def setup_logger():
    log_path = os.path.dirname(os.path.realpath(__file__)) + '/logs'

    if os.path.exists(log_path):
        pass
    else:
        os.mkdir(log_path)

    logging.basicConfig(filename=log_path + '/voip_' + str(datetime.now()).replace(':', '_') + '.log',
                        format='%(asctime)s  %(levelname)s:%(message)s',
                        level=logging.DEBUG)
