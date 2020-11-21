import os
import logging
import asyncio
from datetime import datetime
from vojp import main

log_path = os.getcwd() + '/logs'

if os.path.exists(log_path):
    pass
else:
    os.mkdir(log_path)

logging.basicConfig(filename='logs/voip_' + str(datetime.now()).replace(':', '_') + '.log',
                    format='%(asctime)s  %(levelname)s:%(message)s',
                    level=logging.DEBUG)

try:
    asyncio.run(main.main(), debug=True)
except:
    logging.info(msg='Asyncio event loop has been stopped successfully')
