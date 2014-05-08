#!/usr/bin/env python2


import yumoter

yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')
output = yumoter.syncRepos()

for entry in output:
    print "repo", entry[0]
    print "stdout"
    for line in entry[1]:
        print line
    print "stderr"
    for line in entry[2]:
        print line