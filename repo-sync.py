#!/usr/bin/env python2


import yumoter

yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')
output = yumoter.syncRepos()


print "Repo sync updates\n\n"
for (repo, stdout, stderr) in output:
    print "repo:", repo
    print "stdout:"
    for entry in stdout:
        print "\t%s" % entry
    print "stderr:"
    for entry in stderr:
        print "\t%s" % entry