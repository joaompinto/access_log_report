#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from time import strptime
from time import strftime

fmt_regex, fmt_fields = None, None

FIELDS_MAP = {
    "host": lambda x: x['h'],
    "vhost": lambda x: x['v'],
    "datetime": lambda x: x['t'],
    "url": lambda x: x['r'].split()[1],
    "msec": lambda x: int(x['D']) / 1000,
    'hour': lambda x: strftime('%Y-%m-%d %H:00', x['t']),
    'minute': lambda x: strftime('%Y-%m-%d %H:%M', x['t']),
    'second': lambda x: strftime('%Y-%m-%d %H:%M:%S', x['t']),
    '10minutes': lambda x: strftime('%Y-%m-%d %H:', x['t']) + str(x['t'].tm_min / 10) + "0",
    'size': lambda x: 0 if x['b'] == '-' else int(x['b']),
}


def iso2datetime(date_str):
    # Python < 2.6 does not support %z
    time_str = strptime(date_str[:-6], '%d/%b/%Y:%H:%M:%S')
    # TODO: Handle time zone delta, check input tz vs reporting tz
    # offset = int(date_str[-5:])
    # delta = timedelta(hours=offset / 100)
    # time -= delta
    return time_str


def fmt2regex(fmt):
    """
    :param fmt: access log format specification
    :return: regex, fields : regex = regex for the parsing, fields = list of fields (log format letters)
    """

    # Ignore pre-post processing directives
    fmt = fmt.replace('>', '')
    fmt = fmt.replace('<', '')
    i = 0
    regex = ""
    fields = ""
    while i < len(fmt):
        char = fmt[i]
        next_char = ""
        if i < len(fmt) - 1:
            next_char = fmt[i + 1]
        if char == "%":
            i += 1
            if next_char in 'hvlusbD':
                regex += '(\S+)'
            if next_char == "t":
                regex += '\[(.+)\]'
            if next_char == "r":
                regex += '(.*)'
            fields += next_char
        else:
            regex += char
        i += 1
    regex = regex.replace(' ', '\s')
    return regex, fields


def logline2dict(line):
    """
    :param line: access login line
    :return: dict with the access log line mapped to log format elements
    """
    global fmt_regex, fmt_fields
    line = re.sub('\s+', ' ', line)  # Merge spaces
    line_dict = {}
    line_fields = re.findall(fmt_regex, line)
    if not line_fields:
        print "Ignoring line not matching log format"
        return None
    for i in range(len(fmt_fields)):
        if fmt_fields[i] in "sD":
            line_dict[fmt_fields[i]] = int(line_fields[0][i])
        elif fmt_fields[i] == "t":
            line_dict[fmt_fields[i]] = iso2datetime(line_fields[0][i])
        else:
            line_dict[fmt_fields[i]] = line_fields[0][i]

    return line_dict


def set_log_fmt(log_format):
    global fmt_regex, fmt_fields
    fmt_regex, fmt_fields = fmt2regex(log_format)


def fields(log_dict):
    fields_dict = {}
    for report_field, report_funct in FIELDS_MAP.iteritems():
        fields_dict[report_field] = report_funct(log_dict)
    return fields_dict
