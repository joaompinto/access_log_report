import csv
import sys
import logfile

IT_REQUESTS = 0
IT_TIME = 1
IT_SIZE = 2
IT_TIME_MAX = 3
IT_SIZE_MAX = 4


def summarize_log_data(log_file, config):
    # Returns a list of elements with the following structure:
    #   ( hour,  [vhost_name, [requests, time, size, time_max, size_max]] )
    aggregated_data = {}

    # Setup format logging
    format_str = config.get('format', mandatory=True)[0]
    logfile.set_log_fmt(format_str)

    # Setup replacements
    replacements = config.regex_map('replacements')
    excludes = config.regex_map('excludes')

    line = log_file.readline()
    while line:
        line = line.strip('\n')
        line_dict = logfile.logline2dict(line)
        line_dict = logfile.fields(line_dict)
        line_dict = replacements.apply_to(line_dict)
        if not line_dict:
            line = log_file.readline()
            continue

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

    # Sort data by aggregation key
    aggregated_data = sorted(aggregated_data.iteritems())

    return aggregated_data


def print_results(aggregated_data, options):
    csvwriter = csv.writer(sys.stdout, delimiter=',',
                           quotechar='"', quoting=csv.QUOTE_MINIMAL)

    aggregation_keys = aggregated_data[0][0]
    keys = ['key_' + str(i) for i in range(len(aggregation_keys))]
    csvwriter.writerow(keys + ['requests', 'taken (ms)', 'size', 'taken_max', 'size_max'])
    for aggregation_keys, aggregated_row in aggregated_data:
        csvwriter.writerow(list(aggregation_keys) + aggregated_row)
