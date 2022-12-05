import argparse
from scanner import config, scan

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--config", help="Path to config file", default="config.yaml")
parser.add_argument("-a", "--angle", help="Only scan this angle", required=False)
parser.add_argument("-s", "--start-at", help="Start at this angle", default=0)
args = parser.parse_args()

if __name__ == '__main__':
    config.config_file = args.config
    scan.init()
    if args.angle:
        scan.scan_angle(int(args.angle))
    else:
        scan.scan_from(int(args.start_at))
