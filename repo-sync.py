#!/usr/bin/env python2


import yumoter
import smtplib
import string
from email.mime.text import MIMEText

#yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')
yumoter = yumoter.yumoter('config/repos.json', '/mnt/yum_repos/yumoter/repos')
#yumoter = yumoter.yumoter('config/repos.json', '/vagrant/yumoter/repos')
output = yumoter.syncRepos()

msgBody = []
print "Repo sync updates\n\n"
for (repo, stdout, stderr) in output:
    msgBody.append("repo: %s" % repo)
    msgBody.append("stdout:")
    for entry in stdout:
        msgBody.append("\t%s" % entry)
    msgBody.append("stderr:")
    for entry in stderr:
        msgBody.append("\t%s" % entry)
    msgBody.append("####")

msg = MIMEText('\r\n'.join(msgBody))
smtp = smtplib.SMTP('localhost', 25)
msg["From"] = "yumoter@gorillanation.com"
msg["To"] = "sysadmins@evolvemediallc.com"
msg["Subject"] = "[Repo sync] Updates"
msg.add_header("Content-Type", "text/plain")
smtp.sendmail(msg["From"], msg["To"], msg.as_string())
