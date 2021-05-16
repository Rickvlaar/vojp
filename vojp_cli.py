from vojp.electron_gui_interface import ElectronGuiSettings
import sys
import argparse

cli_parser = argparse.ArgumentParser(prog='gui')
cli_parser.add_argument('-s', '--settings', help='returns default vojp settings', action='store_true')
cli_parser.add_argument('-l', '--latency', help='returns current end-to-end latency', action='store_true')


args = cli_parser.parse_args()
if args.settings:
    print(ElectronGuiSettings().to_json())
if args.latency:
    print('x')
sys.stdout.flush()
