#!/usr/bin/env python2


import yumoter

yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')
output = yumoter.syncRepos()

print "STDOUT"
for entry in output[0]:
	for foo in entry:
		print foo
print "STDERR"
for entry in output[1]:
	print entry