import csv
import sys
import logfile
from os.path import exists
import datetime
from dateutil import parser
from pprint import pprint

IT_REQUESTS = 0
IT_TIME = 1
IT_SIZE = 2
IT_TIME_MAX = 3
IT_SIZE_MAX = 4


def summarize_log_data(log_file, config, options):
    # Returns a list of elements with the following structure:
    #   ( hour,  [vhost_name, [requests, time, size, time_max, size_max]] )
    last_time = current_time = datetime.datetime.now()
    state = config.get('state')
    if state:
        log_file.seek(0, 2)
        file_size = log_file.tell()
        last_position_fname = state[0]
        if not exists(last_position_fname):
            with open(last_position_fname, 'wt') as last_run_file:
                current_time = datetime.datetime.now()
                last_run_file.write("%s %s\n" % (str(file_size), current_time.isoformat()))
            if not options.quiet:
                print "Created initial file position"
            sys.exit(0)
        else:
            with open(last_position_fname, 'rt') as last_run_file:
                last_postion, last_time = last_run_file.readline().split()
                last_postion = int(last_postion)
                last_time = parser.parse(last_time)
                if file_size == last_postion:
                    if not options.quiet:
                        print "File size did not change, nothing to parse."
                    sys.exit(0)
                if file_size < last_postion:  # File was truncated, restart from beginning
                    if not options.quiet:
                        print "File was truncated, restarting from beginning of file"
                    log_file.seek(0)
                else:
                    log_file.seek(last_postion)  # Go to last position
    elapsed_seconds = (current_time - last_time).total_seconds()

    parsed_lines = 0
    aggregated_data = {}

    # Setup format logging
    format_str = config.get('format', mandatory=True)[0]
    logfile.set_log_fmt(format_str)

    # Setup replacements
    replacements = config.regex_map('replacements')

    line = log_file.readline()
    while line:
        line = line.strip('\n')
        line_dict = logfile.logline2dict(line)
        line_dict = logfile.fields(line_dict)
        line_dict = replacements.apply_to(line_dict)
        if not line_dict:
            line = log_file.readline()
            continue
        parsed_lines += 1
        aggregation_key = tuple([line_dict[group_name] for group_name in config.get('group_by')])
        aggregated_row = aggregated_data.get(aggregation_key)
        # Create new key if needed
        if not aggregated_row:
            aggregated_data[aggregation_key] = aggregated_row = [0] * 5

        aggregated_row[IT_REQUESTS] += 1
        time_taken = line_dict['msec']
        response_size = line_dict['size']
        aggregated_row[IT_TIME] += time_taken
        aggregated_row[IT_SIZE] += response_size
        aggregated_row[IT_TIME_MAX] = max(time_taken, aggregated_row[IT_TIME_MAX])
        aggregated_row[IT_SIZE_MAX] = max(response_size, aggregated_row[IT_SIZE_MAX])
        line = log_file.readline()

    # Calculate results
    if options.results:
        resuls_aggregated_data = {}
        for key, row in aggregated_data.iteritems():
            row[IT_TIME] = row[IT_TIME] / row[IT_REQUESTS]
	    row[IT_SIZE] = row[IT_SIZE] / row[IT_REQUESTS]
            row[IT_REQUESTS] = int(row[IT_REQUESTS] / elapsed_seconds * 100) / 100.0
	    

    # Sort data by aggregation key
    aggregated_data = sorted(aggregated_data.iteritems())

    if state:
        last_position_fname = state[0]
        file_size = log_file.tell()
        with open(last_position_fname, 'wt') as last_run_file:
            current_time = datetime.datetime.now()
            last_run_file.write("%s %s\n" % (str(file_size), current_time.isoformat()))

    if not options.quiet:
        print "Processed", parsed_lines
    return aggregated_data


def print_results(aggregated_data, options):
    csvwriter = csv.writer(sys.stdout, delimiter=',',
                           quotechar='"', quoting=csv.QUOTE_MINIMAL)

    aggregation_keys = aggregated_data[0][0]
    keys = ['key_' + str(i) for i in range(len(aggregation_keys))]
    if options.results:
        headers =  keys + ['rps', 'avg (ms)', 'size', 'taken_max', 'size_max']
    else:
        headers = keys + ['requests', 'taken (ms)', 'size', 'taken_max', 'size_max']
    if not options.quiet:
        csvwriter.writerow(headers)
    for aggregation_keys, aggregated_row in aggregated_data:
        csvwriter.writerow(list(aggregation_keys) + aggregated_row)
