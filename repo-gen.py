#!/usr/bin/env python2


import yumoter

yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')
output = yumoter.syncRepos()

print "errors:"
for entry in output:
    print entry[1]