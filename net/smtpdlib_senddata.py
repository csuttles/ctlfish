# smtpd_senddata.py
import smtplib
import email.utils
from email.mime.text import MIMEText

# Create the message
msg = MIMEText('This is the body of the message. Your new user name is victim and your pass is hunter2')
msg['To'] = email.utils.formataddr(('ctlfish', 'ctlfish@ctlfish.org'))
msg['From'] = email.utils.formataddr(('ctlfish', 'ctlfish@ctlfish.org'))
msg['Subject'] = 'Simple test message'

server = smtplib.SMTP('127.0.0.1', 25)
server.set_debuglevel(True)  # show communication with the server
try:
    server.sendmail('ctlfish@ctlfish.org',
                    ['ctlfish@ctlfish.org'],
                    msg.as_string())
finally:
    server.quit()
