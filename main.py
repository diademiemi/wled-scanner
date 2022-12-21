import argparse
from scanner import config, scan
from scanner.calculator import calculate

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--config", help="Path to config file", default="config.yaml")
parser.add_argument("-d", "--debug", help="Enable debug mode", action="store_true")

run_group = parser.add_mutually_exclusive_group()
run_group.add_argument("-S", "--scan", help="Scan the LEDs", action="store_true")
run_group.add_argument("-C", "--compute", help="Compute previously gathered images", action="store_true")

scan_group = parser.add_argument_group("Scan")
scan_group.add_argument("-a", "--angle", help="Only scan this angle in degrees", required=False)
scan_group.add_argument("-s", "--start-at", help="Start at this angle", default=0)

args = parser.parse_args()

if __name__ == '__main__':
    config.config_file = args.config

    if args.scan:
        scan.init()
        if args.angle:
            scan.scan_angle(args.angle)
        else:
            scan.scan_from(args.start_at)
    elif args.compute:
        calculate.compute()
    else:
        parser.print_help()
