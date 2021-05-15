import asyncio
import logging
import argparse
import json
import sys
from vojp.client import UdpClient
from vojp.server import AsyncUdpServer
from vojp.config import Config
from datetime import datetime


async def main():
    setup_logger()

    cli_parser = argparse.ArgumentParser(prog='main')
    cli_parser.add_argument('-s', '--settings', help='pass settings as JSON string and start vojp')
    args = cli_parser.parse_args()

    vojp_settings = dict()
    if args.settings:
        vojp_settings = json.loads(args.settings)
        logging.info(msg='settings received: ' + str(vojp_settings))
        print('settings received: ' + str(json.loads(args.settings)) + '\n starting vojp')
        sys.stdout.flush()
    else:
        vojp_settings = {'ip_address': '127.0.0.1', 'port': '5000', 'packet_length': '10', 'buffer_size': '10',
                         'host_server': 'true', 'echo_mode': 'true', 'record': 'false', 'debug_level': 'INFO',
                         'input_sample_rate': '48000', 'output_sample_rate': '48000', 'input_device': '4',
                         'output_device': '3'}

    # start event loop
    await start_vojp(vojp_settings)

    while True:
        await asyncio.sleep(1)


async def start_vojp(settings):
    logging.getLogger().setLevel(level=settings['debug_level'])
    logging.info(msg='Application started')
    logging.info(msg='Input device id: ' + settings['input_device'])
    logging.info(msg='Output device id: ' + settings['output_device'])

    client = UdpClient(ip=settings['ip_address'],
                       port=int(settings['port']),
                       input_sample_rate=int(settings['input_sample_rate']),
                       output_sample_rate=int(settings['output_sample_rate']),
                       audio_input_device_id=int(settings['input_device']),
                       audio_output_device_id=int(settings['output_device']),
                       record_audio=bool(settings['record'] == 'true'))

    # Start Server if asked
    asyncio_coros = [client.start_client()]
    if bool(settings['host_server'] == 'true'):
        server = AsyncUdpServer(echo_mode=bool(settings['echo_mode'] == 'true'))
        asyncio_coros.append(server.start_server())

    await asyncio.gather(*asyncio_coros)


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
