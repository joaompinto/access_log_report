#!/usr/bin/python
# -*- coding: utf-8 -*-

# Extends with fields with friendly aliases for config specifications
FIELDS_MAP = {
    "vhost": lambda x: x['server_name'],
    "url": lambda x: x['request_url'],
    "msec": lambda x: int(x['time_us']) / 1000,
    'hour': lambda x: x['time_received_datetimeobj'].strftime('%Y-%m-%d %H:00'),
    'minute': lambda x: x['time_received_datetimeobj'].strftime('%Y-%m-%d %H:%M'),
    'second': lambda x:  x['time_received_datetimeobj'].strftime('%Y-%m-%d %H:%M:%S'),
    '10minutes': lambda x:  x['time_received_datetimeobj'].strftime('%Y-%m-%d %H:') + str(x['time_received_datetimeobj'].minute / 10) + "0",
}

def fields(log_dict):
    fields_dict = log_dict
    for report_field, report_func in FIELDS_MAP.iteritems():
        fields_dict[report_field] = report_func(log_dict)
    return fields_dict
