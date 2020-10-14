import asyncio
from gui import Gui
import logging

async def main():
    logging.basicConfig(level=logging.DEBUG)

    # Show Gui
    gui = Gui()
    gui.start_gui()

    while True:
        await asyncio.sleep(50000)


async def shutdown():
    loop = asyncio.get_running_loop()
    tasks = [task for task in asyncio.all_tasks() if task != asyncio.current_task()]
    [task.cancel() for task in tasks]
    done, pending = await asyncio.wait(await asyncio.gather(*tasks, return_exceptions=True))
    loop.stop()


if __name__ == '__main__':

    try:
        asyncio.run(main(), debug=True)
    except:
        # asyncio.get_running_loop().create_task(shutdown())
        print('Loop has been stopped successfully')
