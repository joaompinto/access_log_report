#!/usr/bin/python
# -*- coding: utf-8 -*-


from optparse import OptionParser
import accounting
import sys
from config import Config


def parse_args():
    cmd_parser = OptionParser()

    (options, args) = cmd_parser.parse_args()
    if len(args) < 2:
        cmd_parser.print_help()
        sys.exit(1)
    return options, args


def main():
    (options, args) = parse_args()
    cfg_filename = args[0]
    config = Config(cfg_filename)
    access_log_filename = args[1]
    log_file = open(access_log_filename)
    aggregated_data = accounting.summarize_log_data(log_file, config)
    accounting.print_results(aggregated_data, config)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "Interrupted"
