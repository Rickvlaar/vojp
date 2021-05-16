import asyncio
import logging
import argparse
import json
import sys
from vojp.client import UdpClient
from vojp.server import AsyncUdpServer
from vojp.config import Config
from vojp.electron_gui_interface import ElectronGuiSettings
from datetime import datetime


async def main():
    setup_logger()

    cli_parser = argparse.ArgumentParser(prog='main')
    cli_parser.add_argument('-s', '--settings', help='pass settings as JSON string and start vojp')
    args = cli_parser.parse_args()

    vojp_settings = ElectronGuiSettings()
    if args.settings:
        vojp_settings.read_from_electron(args.settings)
        logging.info(msg='settings received: ' + str(vojp_settings))
        print('settings received: ' + args.settings + '\n starting vojp')
        sys.stdout.flush()
    else:
        test_settings = json.dumps(
                {'ip_address'       : '127.0.0.1', 'port': '5000', 'packet_length': '10', 'buffer_size': '10',
                 'host_server'      : 'true', 'echo_mode': 'true', 'record': 'false', 'debug_level': 'DEBUG',
                 'input_sample_rate': '48000', 'output_sample_rate': '48000', 'input_device': '0',
                 'output_device'    : '1'})
        vojp_settings.read_from_electron(test_settings)
    vojp_settings.save_config_ini()

    # start event loop
    await start_vojp(vojp_settings)

    while True:
        await asyncio.sleep(1)


async def start_vojp(settings):
    logging.getLogger().setLevel(level=settings.debug_level.value)
    logging.info(msg='Application started')
    logging.info(msg='Input device id: ' + str(settings.input_device.value))
    logging.info(msg='Output device id: ' + str(settings.output_device.value))

    client = UdpClient(ip=settings.ip_address.value,
                       port=settings.port.value,
                       input_sample_rate=settings.input_sample_rate.value,
                       output_sample_rate=settings.output_sample_rate.value,
                       audio_input_device_id=settings.input_device.value,
                       audio_output_device_id=settings.output_device.value,
                       record_audio=settings.record.value)

    # Start Server if asked
    asyncio_coros = [client.start_client()]
    if settings.host_server.value:
        server = AsyncUdpServer(echo_mode=settings.echo_mode.value)
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


if __name__ == '__main__':
    try:
        asyncio.run(main(), debug=False)
    except Exception:
        logging.info(msg='Asyncio event loop has been stopped successfully')
        logging.exception(msg='Asyncio event loop has been stopped successfully')
