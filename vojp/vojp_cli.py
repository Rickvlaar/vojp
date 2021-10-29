from electron_gui_interface import ElectronGuiSettings
import sys
import argparse

cli_parser = argparse.ArgumentParser(prog='main')
cli_parser.add_argument('-g', '--get', help='returns default vojp settings', action='store_true')

#
# # args = cli_parser.parse_args()
# if args.get:
#     print(ElectronGuiSettings().to_json())
# sys.stdout.flush()
