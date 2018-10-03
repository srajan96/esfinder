import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime
import sendgrid
import os
from sendgrid.helpers.mail import *
import pytz
tz = pytz.timezone('Asia/Kolkata')

today = datetime.now().astimezone(tz).date()

batchdict = {
'CERED-10':{ 
  'email-list':['srajan1996@gmail.com','chetangsti@gmail.com'],
  'last-message':''
},
# 'CERMD-04':{ 
#   'email-list':['srajan1996@gmail.com'],
#   'last-message':''
# },

'CERED-04': {
  'email-list':['nikhilpvp6@gmail.com','srajan1996@gmail.com'],
  'last-message':''
}
}

def sendemail(emaillist,batch, email_content):
    for email in emaillist:
        sg =sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email('iesinformer@srajanlabs.com')
        to_email = Email(email)
        subject = 'New Notification from IESMASTERS for batch '+batch
        content = Content('text/html', email_content)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print ("Mail sent to "+email)

def addemail(batch, email):
    batchdict[batch].append(email)

sched = BlockingScheduler()

@sched.scheduled_job('cron',hour=0,timezone="Asia/Kolkata")
def clear_last_message():
    print("Clearing last message started")
    for batch in batchdict:
        batchdict[batch]['last-message']=''
        print("Last messaage for batch ",batch," is ",batchdict[batch]['last-message'])

    print("Cleared all last messages")
    

@sched.scheduled_job('interval', hours=2,timezone="Asia/Kolkata")
def scheduled_job():
    print("Process started")
    print(datetime.now().astimezone(tz))
    response = urlopen('https://iesmaster.org/')
    html = response.read()
    soup=BeautifulSoup(html,'html5lib')
    news = soup.find('div', {'id': 'newser'}).ul
    for child in news:
        if str(type(child)) == "<class 'bs4.element.Tag'>":
            url = child.a['href']
            
            date = datetime.strptime(child.find_all(class_='ns-dt')[0].contents[0],'%d-%m-%y').astimezone(tz).date()

    #         print(url)

            if not  date < today:
                print ('############New Notification#############')
                child.a.i.extract()
                child.a.span.extract()
                desc = child.a.contents[0]
                print (desc)
                first_notif=True
                new_notif=False
                for batch in batchdict:
                    splitter = batch.split('-')
                    (name, code) = (splitter[0], splitter[1])
                    print ("Cheking for batch ",name,code)
                    print("Batch last seen message is ",batchdict[batch]['last-message'])                    
                    first_notif=True
                    loop_first_notif=""
                    new_notif=False
                    if(batchdict[batch]['last-message']==desc):
                      print("___________MAIL ALREADY SENT,SKIPPING REMAINING________")
                      continue
                    else:
                      new_notif=True
                      if(first_notif):
                        loop_first_notif=desc
                        first_notif=False

                    if desc.find(str(batch)) > 0 or desc.find(name) > 0 \
                        and desc.find(code) > 0:
                        print("-------------SENDING EMAIL-----------")
                        print ("DESCRIPTION : ",desc)
                        content = \
                            'IES Master added a new notification.See it here <br>'
                        content += \
                            "<a href='https://drive.google.com/viewer?url=" \
                            + url + "'>" + desc + '</a>'

                        sendemail(batchdict[batch]['email-list'],batch, content)
                        print("-------------MAIL SENDING OVER--------")
                        if new_notif:
                          batchdict[batch]['last-message']=loop_first_notif
                print("###########################################")
#         print("==========")

####
# MAIN PROGRAM
####

sched.start()
print("Program execution started")
# scheduled_job()
