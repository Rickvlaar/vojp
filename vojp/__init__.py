import os
import logging
import asyncio
from database import util
from vojp.config import Config
from vojp import main

if os.path.exists(Config.RECORDING_DIR):
    pass
else:
    os.mkdir(Config.RECORDING_DIR)


if os.path.exists(Config.LOG_DIR):
    pass
else:
    os.mkdir(Config.LOG_DIR)

if not util.check_data_model():
    util.create_data_model()

try:
    asyncio.run(main.main(), debug=False)
except:
    logging.info(msg='Asyncio event loop has been stopped successfully')
