import configparser
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
from email.header import Header
from email.mime.base import MIMEBase
from email import encoders
from email.mime.image import MIMEImage
import shutil
config = configparser.ConfigParser()
config.read('config.ini')

# mail
email_to = "danson_tsui@phison.com"
email_cc = "danson_tsui@phison.com"
email_from = "no-reply.logParser@phison.com"

def mailForUpdateTimeoutSetting(maillist,subject,htmlcontent):
   
    msg = MIMEMultipart('related')
    msg.attach(MIMEText(htmlcontent, 'html', 'utf-8'))


    if len(htmlcontent) >0:
        part = MIMEText(htmlcontent, 'html', _charset="UTF-8")
        msg.attach(part)

    msg['From'] = 'no-reply.report@phison.com'
    msg['To'] = maillist
    msg['Subject'] = Header(subject,'utf-8').encode()

    #server = smtplib.SMTP('mail.phison.com', 25)
    server = server = smtplib.SMTP('192.168.1.3', 25)
    server.ehlo()
    server.starttls()
    server.sendmail(maillist, maillist.split(','), msg.as_string())
    server.quit()

def removefile(movefolder, orifile):
    try:
        s1 = orifile.split('\\')
        s = s1[len(s1) - 1]
        fpath = movefolder + "\\" + s
        shutil.move(orifile, fpath)
    except Exception as e:
        print(str(e))
#把image 內嵌到mail裡面 ,這樣 webmail才看得到 否則只有outlook看得到圖片
def mailReportContentID(maillist,ImgFileName,listImage,subject,savepath,htmlcontent,detaillist):
    
    secondStartId = len(ImgFileName)+1
    msg = MIMEMultipart('related')

    msg_str = subject + "<br>file path : "+ savepath +"\n"
    msg_str += htmlcontent


    for i in range(0,len(ImgFileName)):
        msg_str += '<br><img src="cid:'+str(i)+'" >\n'
    for i in range(0,len(listImage)):
        msg_str += '<br><img src="cid:'+str(secondStartId+i)+'" width="1200" height="1800">\n'        
                   #"<p><img src="cid:" 0?=""></p>"
    msg.attach(MIMEText(msg_str, 'html', 'utf-8'))
    for i in range(0,len(ImgFileName)):        
        with open(savepath+"\\"+ImgFileName[i],'rb') as f:
            pic = MIMEImage(f.read())
            pic.add_header('Content-ID','<'+str(i)+'>\n')
            msg.attach(pic)

    for i in range(len(listImage)):        
        with open(savepath+"\\"+listImage[i],'rb') as f:
            pic = MIMEImage(f.read())
            pic.add_header('Content-ID','<'+str(secondStartId+i)+'>\n')
            msg.attach(pic)

    if len(htmlcontent) >0:
        part = MIMEText(htmlcontent, 'html', _charset="UTF-8")
        msg.attach(part)
        
    for i in range(0,len(detaillist)):
        msg_str += "<br>"+ detaillist[i]+"\n"  
    msg['From'] = 'no-reply.report@phison.com'
    msg['To'] = maillist
    msg['Subject'] = Header(subject,'utf-8').encode()

    #server = smtplib.SMTP('mail.phison.com', 25)
    server = server = smtplib.SMTP('192.168.1.3', 25)
    server.ehlo()
    server.starttls()
    server.sendmail(maillist, maillist.split(','), msg.as_string())
    server.quit()

def send_mail2(receivers, exMessage):
    # ['[email protected],[email protected]']
    # receivers = ['[danson_tsui@phison.com],[brian_huang@phison.com],[kelvin_lam@phison.com],[jasper_lin@phison.com],[allen_lin@phison.com],[ck_zhang@phison.com]']
    #receivers = 'danson_tsui@phison.com,brian_huang@phison.com,jasper_lin@phison.com,allen_lin@phison.com,ck_zhang@phison.com,kelvin_lam@phison.com,ben_lin@phison.com'
    email_to1 = receivers 
    # email_to1 =  ["danson_tsui@phison.com","brian_huang@phison.com","kelvin_lam@phison.com","jasper_lin@phison.com","allen_lin@phison.com","ck_zhang@phison.com"]
    # email_cc = "lacie_wu@phison.com"
    email_cc1 = "danson_tsui@phison.com"
    email_from1 = "danson_tsui@phison.com"

    msg = MIMEMultipart()
    msg["From"] = email_from1
    msg["To"] = email_to1
    msg["CC"] = email_cc1
    # rcep = [email_cc] + email_to.split(",")
    # --- Email  Subject ---
    msg["Subject"] = "[my stock info] "
    msg["preamble"] = 'You will not see this in a MIME-aware mail reader.\n'

    # ----- Email  Message -----
    part = MIMEText(f"{exMessage}", 'html', _charset="UTF-8")
    msg.attach(part)

    # --- 寄件的 SMTP mail server ---
    server = smtplib.SMTP('mail.phison.com', 25)
    server.ehlo()
    server.starttls()
    server.sendmail(email_from, receivers.split(','), msg.as_string())
    server.quit()


def send_mail1(logfolder, exMessage):
    # ['[email protected],[email protected]']
    # receivers = ['[danson_tsui@phison.com],[brian_huang@phison.com],[kelvin_lam@phison.com],[jasper_lin@phison.com],[allen_lin@phison.com],[ck_zhang@phison.com]']
    receivers = 'danson_tsui@phison.com,brian_huang@phison.com,jasper_lin@phison.com,allen_lin@phison.com,ck_zhang@phison.com,kelvin_lam@phison.com,ben_lin@phison.com'
    email_to1 = "danson_tsui@phison.com;brian_huang@phison.com;jasper_lin@phison.com;allen_lin@phison.com;ck_zhang@phison.com;kelvin_lam@phison.com;ben_lin@phison.com"
    # email_to1 =  ["danson_tsui@phison.com","brian_huang@phison.com","kelvin_lam@phison.com","jasper_lin@phison.com","allen_lin@phison.com","ck_zhang@phison.com"]
    # email_cc = "lacie_wu@phison.com"
    email_cc1 = "lacie_wu@phison.com"
    email_from1 = "no-reply.logParser@phison.com"

    msg = MIMEMultipart()
    msg["From"] = email_from1
    msg["To"] = email_to1
    msg["CC"] = email_cc1
    # rcep = [email_cc] + email_to.split(",")
    # --- Email  Subject ---
    msg["Subject"] = "[tool version list] "
    msg["preamble"] = 'You will not see this in a MIME-aware mail reader.\n'

    # ----- Email  Message -----
    part = MIMEText(u"sstek offline tool ver List: " + "\n" + exMessage, 'html', _charset="UTF-8")
    msg.attach(part)

    # --- 寄件的 SMTP mail server ---
    #server = smtplib.SMTP('mail.phison.com', 25)
    server = smtplib.SMTP('192.168.1.3', 25)
    server.ehlo()
    server.starttls()
    server.sendmail(email_from, receivers.split(','), msg.as_string())
    server.quit()

'''
def send_mail(logfolder, exMessage):
    msg = MIMEMultipart()
    msg["From"] = email_from
    msg["To"] = email_to
    msg["CC"] = email_cc
    rcep = [email_cc] + email_to.split(",")
    # --- Email  Subject ---
    msg["Subject"] = "[databaseParser] An exception occurred"
    msg["preamble"] = 'You will not see this in a MIME-aware mail reader.\n'

    # ----- Email  Message -----
    part = MIMEText(u"logfolder: " + logfolder + "\n" + exMessage, _charset="UTF-8")
    msg.attach(part)

    # --- 寄件的 SMTP mail server ---
    server = smtplib.SMTP('mail.phison.com', 25)
    server.ehlo()
    server.starttls()
    server.sendmail(email_from, rcep, msg.as_string())
    server.quit()
'''


def mailReportCsv(maillist,subject,savepath,fileToSend):
    msg = MIMEMultipart('related')

    msg_str = subject + "<p>file path : "+ savepath +"</p>\n"
    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)    
    msg.attach(MIMEText(msg_str, 'html', 'utf-8'))
    fp = open(fileToSend, "rb")
    attachment = MIMEBase(maintype, subtype)
    attachment.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)
    #with open(savepath+"\\yeild_example.png",'rb') as f:
    #        pic = MIMEImage(f.read())
    #        pic.add_header('Content-ID','<'+str(1001)+'>\n')
    #        msg.attach(pic)

    msg['From'] = 'no-reply.report@phison.com'
    msg['To'] = maillist
    msg['Subject'] = Header(subject,'utf-8').encode()

    server = smtplib.SMTP('mail.phison.com', 25)
    server.ehlo()
    server.starttls()
    server.sendmail(maillist, maillist.split(','), msg.as_string())
    server.quit()


def send_mail(mailto, mailcc, mailfrom, Subject, exMessage):
    mime = MIMEText(exMessage, "html", "utf-8")
    mime["Subject"] = Subject
    mime["From"] = mailfrom
    mime["To"] = mailto
    mime["CC"] = mailcc
    rcep = [mailcc] + mailto.split(",")
    msg = mime.as_string()
    # --- 寄件的 SMTP mail server ---
    server = smtplib.SMTP(config['mailServer']['server'], int(config['mailServer']['port']))
    server.ehlo()
    server.starttls()
    # server.login('sstek_report', 'hv28131094!')
    status = server.sendmail(mailfrom, rcep, msg)
    print(status)
    server.quit()