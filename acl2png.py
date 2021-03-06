#!/bin/sh
from optparse import OptionParser
from config import Config
import chart
import sys


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
    csv_filename = args[1]
    chart_sections = [section for section in config.config_dict.iterkeys() if section.endswith('_chart')]
    for chart_name in chart_sections:
        data = chart.build_chart_data(csv_filename, config)
        chart.create_chart(data, chart_name, config)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "Interrupted"
