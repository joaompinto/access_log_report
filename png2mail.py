#!/usr/bin/python
# -*- coding: utf-8 -*-


# Code from http://stackoverflow.com/a/920928/401041

# Send an HTML email with an embedded image and a plain text message for
# email clients that don't want to display the HTML.
import sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from config import Config
from optparse import OptionParser


def attach_image(msgRoot, image_id, filename):
    # This example assumes the image is in the current directory
    fp = open(filename, 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()

    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<%s>' % image_id)
    msgRoot.attach(msgImage)


def send_mime_mail(config):

    html_report = '\n'.join(config.get('body_html'))

    images = {}

    for line  in config.get('images'):
        image_id, image_fname = line.split()
        images[image_id] = image_fname


    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = config.get('Subject')[0]
    msgRoot['From'] = config.get('From')[0]
    msgRoot['To'] = config.get('To')[0]
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    msgText = MIMEText('This is the alternative plain text message.')
    msgAlternative.attach(msgText)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText(html_report, 'html')
    msgAlternative.attach(msgText)

    for image_id, filename in images.iteritems():
        attach_image(msgRoot, image_id, filename)


    # Send the email (this example assumes SMTP authentication is required)
    import smtplib

    smtp = smtplib.SMTP()
    smtp.connect(config.get('smtp_server')[0])
    smtp.sendmail(config.get('From')[0], config.get('To')[0].split(','), msgRoot.as_string())
    smtp.quit()

def parse_args():
    cmd_parser = OptionParser()
    (options, args) = cmd_parser.parse_args()

    return options, args

def main():
    (options, args) = parse_args()
    cfg_filename = args[0]
    config = Config(cfg_filename)
    send_mime_mail(config)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "Interrupted"

