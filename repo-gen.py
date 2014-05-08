#!/usr/bin/env python2


import yumoter

yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')
output = yumoter.syncRepos()

print "STDOUT"
for entry in output[0]:
	print entry
print "STDERR"
for entry in output[1]:
	print entry