#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import sys

from optparse import OptionParser
import accounting
from config import Config


def parse_args():
    cmd_parser = OptionParser()

    cmd_parser.add_option("-q", "--quiet", dest="quiet",
        help="No information ouput", action="store_true", default=False)
    cmd_parser.add_option("-r", "--results", dest="results",
        help="Calculate perofrmance results", action="store_true", default=False)
    (options, args) = cmd_parser.parse_args()

    return options, args


def main():
    (options, args) = parse_args()
    cfg_filename = args[0]
    config = Config(cfg_filename)
    log_fname = config.get('log')
    if len(args) > 1:
        access_log_filename = args[1]
    else:
        access_log_filename = log_fname[0]
    log_file = open(access_log_filename)
    aggregated_data = accounting.summarize_log_data(log_file, config, options)
    accounting.print_results(aggregated_data, options)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "Interrupted"
