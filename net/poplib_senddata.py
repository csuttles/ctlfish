import poplib

M = poplib.POP3('127.0.0.1')
M.user('victim')
M.pass_('hunter2')
numMessages = len(M.list()[1])
for i in range(numMessages):
    for j in M.retr(i+1)[1]:
        print(j)# smtpd_senddata.py
