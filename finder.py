#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

# !{sys.executable} -m pip install sendgrid

from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime
import sendgrid
import os
from sendgrid.helpers.mail import *
today = datetime.now().date()

# print(type(today))

# print(os.environ.get('SENDGRID_API_KEY'))
# today=now.strftime("%d-%m-%y")

###HELPERS###

batchdict = {
  'CERED-10': ['chetangsti@gmail.com','srajan1996@gmail.com'], 'CERED-04': ['nikhilpvp6@gmail.com']}


def sendemail(emaillist, email_content):
    for email in emaillist:
        sg = \
            sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'
                ))
        from_email = Email('iesinformer@srajanlabs.com')
        to_email = Email(email)
        subject = 'New Notificatison from IESMASTERS for you'
        content = Content('text/html', email_content)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print (response.status_code)


def addemail(batch, email):
    batchdict[batch].append(email)


sched = BlockingScheduler()


@sched.scheduled_job('interval', hours=12)
def scheduled_job():
	print("Process started")
    response = urlopen('https://iesmaster.org/')
    html = response.read()

    soup = BeautifulSoup(html, 'html5lib')
    news = soup.find('div', {'id': 'newser'}).ul
    for child in news:
        if str(type(child)) == "<class 'bs4.element.Tag'>":

    #         print("----------")
    #         print(child)

            url = child.a['href']
            date = datetime.strptime(child.find_all(class_='ns-dt'
                    )[0].contents[0], '%d-%m-%y').date()

    #         print(url)

            if not date < today:
                print ('New Notification')
                child.a.i.extract()
                child.a.span.extract()
                desc = child.a.contents[0]
                print (desc)
                for batch in batchdict:
                    splitter = batch.split('-')
                    (name, code) = (splitter[0], splitter[1])
                    print (name, code)
                    if desc.find(str(batch)) > 0 or desc.find(name) > 0 \
                        and desc.find(code) > 0:
                        print (desc)
                        content = \
                            'IES Master added a new notification.See this <br>'
                        content += \
                            "<a href='https://drive.google.com/viewer?url=" \
                            + url + "'>" + desc + '</a>'

                        sendemail(batchdict[batch], content)

    #         print("==========")

####
# MAIN PROGRAM
####

sched.start()

# scheduled_job()
