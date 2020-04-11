import imaplib

M = imaplib.IMAP4(host='127.0.0.1', port=143)
M.login('victim', 'hunter2')
M.select()
typ, data = M.search(None, 'ALL')
for num in data[0].split():
    typ, data = M.fetch(num, '(RFC822)')
    print('Message %s\n%s\n' % (num, data[0][1]))
M.close()
M.logout()
