#!/usr/bin/python
# -*- coding: utf-8 -*-


# Code from http://stackoverflow.com/a/920928/401041

# Send an HTML email with an embedded image and a plain text message for
# email clients that don't want to display the HTML.

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

# Define these once; use them twice!
strFrom = 'From'
strTo = 'To'
strSubject = 'Report'

HTML_REPORT = """
Daily Report<br>
<img src="cid:image1"><br>
<img src="cid:image2">
"""
images = { 
	'image1' : 'image1.png', 
	'image2' : 'image2.png',
	}

def attach_image(msgRoot, image_id, filename):
	# This example assumes the image is in the current directory
	fp = open(filename, 'rb')
	msgImage = MIMEImage(fp.read())
	fp.close()

	# Define the image's ID as referenced above
	msgImage.add_header('Content-ID', '<%s>' % image_id)
	msgRoot.attach(msgImage)

# Create the root message and fill in the from, to, and subject headers
msgRoot = MIMEMultipart('related')
msgRoot['Subject'] = strSubject
msgRoot['From'] = strFrom
msgRoot['To'] = strTo
msgRoot.preamble = 'This is a multi-part message in MIME format.'

# Encapsulate the plain and HTML versions of the message body in an
# 'alternative' part, so message agents can decide which they want to display.
msgAlternative = MIMEMultipart('alternative')
msgRoot.attach(msgAlternative)

msgText = MIMEText('This is the alternative plain text message.')
msgAlternative.attach(msgText)

# We reference the image in the IMG SRC attribute by the ID we give it below
msgText = MIMEText(HTML_REPORT, 'html')
msgAlternative.attach(msgText)


for image_id, filename in images.iteritems():
	attach_image(msgRoot, image_id, filename)


# Send the email (this example assumes SMTP authentication is required)
import smtplib
smtp = smtplib.SMTP()
smtp.connect('localhost')
smtp.sendmail(strFrom, strTo, msgRoot.as_string())
smtp.quit()

