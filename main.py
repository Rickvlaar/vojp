import asyncio
import logging
from vojp.gui import Gui
from vojp.config import Config
from datetime import datetime


async def main():
    setup_logger()
    # Show Gui
    gui = Gui()
    gui.start_gui()

    while True:
        await asyncio.sleep(1)


async def shutdown():
    logging.info(msg='Shutting down asyncio event loop')
    loop = asyncio.get_running_loop()
    tasks = [task for task in asyncio.all_tasks() if task != asyncio.current_task()]
    [task.cancel() for task in tasks]
    done, pending = await asyncio.wait(await asyncio.gather(*tasks, return_exceptions=True))
    loop.stop()


def setup_logger():
    logging.basicConfig(filename=Config.LOG_DIR + '/voip_' + str(datetime.now()).replace(':', '_') + '.log',
                        format='%(asctime)s  %(levelname)s:%(message)s',
                        level=logging.DEBUG)


try:
    asyncio.run(main(), debug=False)
except:
    logging.info(msg='Asyncio event loop has been stopped successfully')
    logging.exception(msg='Asyncio event loop has been stopped successfully')
