#!/usr/bin/python
# -*- coding: utf-8 -*-

# The access log regex building and line parsing code was adapted from wtop:
#      https://pypi.python.org/pypi/wtop/

import re
from time import strptime
from time import strftime

fmt_regex, fmt_fields = None, None

# translate log format string into a column list and regexp
re_str = r"(\S+)"
re_str_skipped = r"\S+"
re_quot = r'((?:(?<![\\\])(?=[\\\][\\\])*[\\\]"|[^"])*)'
re_quot_skipped = r'(?:(?<![\\\])(?=[\\\][\\\])*[\\\]"|[^"])*'
re_ts = r"\[?(\S+(?:\s+[\-\+]\d+)?)\]?"
re_ts_skipped = r"\[?\S+(?:\s+[\-\+]\d+)?\]?"
re_req = r"(\S+ \S+ \S+)"
re_req_skipped = r"\S+ \S+ \S+"

# {DIRECTIVE_SYMBOL: (FIELD_NAME, REGEX_WHEN_NEEDED, REGEX_WHEN_SKIPPED)}
LOG_DIRECTIVES = {
    # ip is an odd one, since the default Apache is %h but
    "h": ("ip", re_str, re_str_skipped),
    # HostnameLookups changes its content and %a is ALSO the ip. bleh.
    "a": ("ip", re_str, re_str_skipped),
    "A": ("lip", re_str, re_str_skipped),  # server (local) IP
    "l": ("auth", re_str, re_str_skipped),
    "u": ("username", re_str, re_str_skipped),
    "t": ("timestamp", re_ts, re_ts_skipped),
    "r": ("request", re_req, re_req_skipped),
    "m": ("method", re_str, re_str_skipped),
    "D": ("msec", re_str, re_str_skipped),
    "F": ("fbmsec", re_str, re_str_skipped),
    "q": ("query", re_str, re_str_skipped),
    "s": ("status", re_str, re_str_skipped),
    "b": ("bytes", re_str, re_str_skipped),
    "B": ("bytes", re_str, re_str_skipped),
    "O": ("bytes", re_str, re_str_skipped),
    "I": ("bytes_in", re_str, re_str_skipped),
    "v": ("domain", re_str, re_str_skipped),  # Host header
    # actual vhost. May clobber %v
    "V": ("domain", re_str, re_str_skipped),
    "p": ("port", re_str, re_str_skipped),
    # todo: need generic %{foo}X parsing?
    "{ratio}n": ("ratio", re_quot, re_quot_skipped),
    "{host}i": ("host", re_quot, re_quot_skipped),
    "{referer}i": ("ref", re_quot, re_quot_skipped),
    "{user-agent}i": ("ua", re_quot, re_quot_skipped),
    "{x-oracle-dms-ecid}o": ("ecid", re_quot, re_quot_skipped),
    "ignore": ("ignore", re_str, re_str_skipped),
    "ignorequot": ("ignore", re_quot, re_quot_skipped),
}

FIELDS_MAP = {
    "host": lambda x: x['ip'],
    "vhost": lambda x: x['domain'],
    "datetime": lambda x: x['timestamp'],
    "url": lambda x: x['request'].split()[1] if x['request'].count(" ") else '',
    "msec": lambda x: int(x['msec']) / 1000,
    'hour': lambda x: strftime('%Y-%m-%d %H:00', x['timestamp']),
    'minute': lambda x: strftime('%Y-%m-%d %H:%M', x['timestamp']),
    'second': lambda x: strftime('%Y-%m-%d %H:%M:%S', x['timestamp']),
    '10minutes': lambda x: strftime('%Y-%m-%d %H:', x['timestamp']) + str(x['timestamp'].tm_min / 10) + "0",
    'size': lambda x: 0 if x['bytes'] == '-' else int(x['bytes']),
}


def iso2datetime(date_str):
    # Python < 2.6 does not support %z
    time_str = strptime(date_str[:-6], '%d/%b/%Y:%H:%M:%S')
    # TODO: Handle time zone delta, check input tz vs reporting tz
    # offset = int(date_str[-5:])
    # delta = timedelta(hours=offset / 100)
    # time -= delta
    return time_str


# given an Apache LogFormat string and an optional list of relevant fields,
# returns a regular expression that will parse the equivalent log line and
# extract the necessary fields.
def format2regexp(fmt, relevant_fields=()):
    re_d = re.compile("%[\>\<\!,\d]*([\}\{\w\-]+)")
    directives = [x.lower() if '{' in x else x for x in re_d.findall(fmt)]
    # directives = map(lcase, re_d.findall(fmt))
    colnames = list()
    pat = fmt
    for k in directives:
        if k not in LOG_DIRECTIVES and not k.find("{") > -1:
            continue

        field, pattern, skip_pattern = LOG_DIRECTIVES[k]
        atom = pattern
        if (not relevant_fields) or (field in relevant_fields):
            colnames.append(field)
        else:
            atom = skip_pattern

        if k.find("{") > -1:
            p = re.compile("%[\>\<\!,\d]*" + k.replace("}",
                                                       ".").replace("{", "."), re.I)
            pat = p.sub(atom, pat, re.I)
        else:
            pat = re.sub("%[\>\<\!,\d]*" + k, atom, pat)

    leftover = re_d.findall(pat)
    if leftover:
        warn("unrecognized format directives: %%%s" % ", %".join(leftover))

    return pat, colnames


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
        return None

    for i in range(len(fmt_fields)):
        if fmt_fields[i] == "timestamp":
            line_dict[fmt_fields[i]] = iso2datetime(line_fields[0][i])
        else:
            line_dict[fmt_fields[i]] = line_fields[0][i]

    for report_field, report_funct in FIELDS_MAP.iteritems():
        line_dict[report_field] = report_funct(line_dict)

    return line_dict


def set_log_fmt(log_format):
    global fmt_regex, fmt_fields
    fmt_regex, fmt_fields = format2regexp(log_format)
