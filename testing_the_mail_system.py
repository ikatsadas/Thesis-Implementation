import sys
import os
import traceback




def emailThis(to, subject="", body="", files=[]):
    try:
        fro = "ykatsadas@gmail.com"
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email.mime.text import MIMEText
        from email.utils import COMMASPACE, formatdate
        from email import encoders
        msg = MIMEMultipart()
        msg['From'] = fro
        msg['To'] = to
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject
        msg.attach(MIMEText(body))
        for file in files:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(file, "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
            msg.attach(part)
        smtp = smtplib.SMTP("smtp.gmail.com",587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(fro,sys.argv[5])#argument no.5 is the password
        smtp.sendmail(fro, to, msg.as_string())
        smtp.close()
        return True
    except: traceback.print_exc()

try:
    raise Exception('This is the exception you expect to handle')
except:
    var=traceback.format_exc()
    text="The script has finished, chech the log file for more info"+var
    emailThis("johnkats5896@gmail.com", subject="Script finished", body=text)

