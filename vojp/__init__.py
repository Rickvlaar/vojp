import logging
import asyncio
from vojp import main

try:
    asyncio.run(main.main(), debug=False)
except:
    logging.info(msg='Asyncio event loop has been stopped successfully')
