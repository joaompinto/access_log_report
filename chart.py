
import matplotlib
matplotlib.use('Agg')

import csv
from matplotlib.pyplot import *
import matplotlib.dates as mdates
from dateutil import parser
import PIL.Image

COLUMNS_MAP = {
    'rps': 1,
    'avg_msec': 2,
}

TIME_MAP = {'hour': 60*60, '10minutes': 60*10, None: None}


def build_chart_data(csvfilename, config):
    time_interval = None
    max_rps = 0
    minimal_rps = config.get('minimal_rps')
    minimal_rps = float(minimal_rps[0]) if minimal_rps else 0


    for time_str, time_interval in TIME_MAP.iteritems():
        if time_str in config.get('group_by'):
            break

    if time_interval is None:
        raise Exception("Unable to identify time interval")

    with open(csvfilename, 'rb') as csvfile:
        cvsreader = csv.reader(csvfile, delimiter=',', quotechar='"')

        data = {}
        for row in cvsreader:
            ts, vhost, requests, taken, size, taken_nax, size_max = row
            if ts == 'key_0':
                continue
            data_row = data.get(vhost, [])
            rps = float(requests) / float(time_interval)
            avg_msec = float(taken) / float(requests)
            if minimal_rps and rps < minimal_rps:
                avg_msec = 0
            #if rps < 10.0:
            #    max_rps = max(rps, max_rps)
            #    avg_msec = 0
            data_row.append((parser.parse(ts), rps, avg_msec))
            data[vhost] = data_row

    sorted_data = sorted(data.iteritems())
    return sorted_data


def create_chart(data, chart_name, config):
    g_title, value_field, value_label, output_fname_prefix = config.get(chart_name)

    time_str = None
    for time_str, time_interval in TIME_MAP.iteritems():
        if time_str in config.get('group_by'):
            break

    if time_str == "hour":
        g_title += " [hour]"
    if time_str == "10minutes":
        g_title += " [10 minutes]"

    data_column = COLUMNS_MAP.get(value_field)
    if not data_column:
        raise Exception("Data column '%s' is unknown!" % data_column)
    title(g_title)
    ylabel(value_label)

    fig = figure(1)
    ax = fig.add_subplot(111)

    # These are the "Tableau 20" colors as RGB.
    tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                 (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                 (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                 (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                 (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

    # Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
    for i in range(len(tableau20)):
        r, g, b = tableau20[i]
        tableau20[i] = (r / 255., g / 255., b / 255.)

    # Remove the plot frame lines. They are unnecessary chartjunk.
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Ensure that the axis ticks only show up on the bottom and left of the plot.
    # Ticks on the right and top of the plot are generally unnecessary chartjunk.
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    # SEt the date format
    fmt = mdates.DateFormatter('%d/%m - %H:%M')
    # loc = mdates.HourLocator()
    ax = axes()
    ax.xaxis.set_major_formatter(fmt)
    # ax.xaxis.set_major_locator(loc)
    grid(True)

    color_i = 0
    for vhost, values in data:
        x_values = [i[0] for i in values]
        y_values = [i[data_column] for i in values]

        # Plot each line separately with its own color, using the Tableau 20
        # color set in order.
        plot(x_values,
             y_values,
             lw=2.5, color=tableau20[color_i])
        color_i += 1

    # Set legend labels
    color_i = 0
    for vhost, values in data:
        plot([], [], color=tableau20[color_i], linewidth=5, label=vhost)
        color_i += 1

    fig.autofmt_xdate()
    legend(prop={'size': 8}, loc='upper left')

    setp(ax.get_xticklabels(), fontsize=8)
    output_filename = output_fname_prefix+"_"+time_str+".png"
    savefig(output_filename)
    im = PIL.Image.open(output_filename)
    new_img = im.convert('P')
    im.close()
    new_img.save(output_filename)
    close()
