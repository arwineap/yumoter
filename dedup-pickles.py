#!/usr/bin/env python2


import os
import sys
import pickle

filelist = []
for lsname in os.listdir('./'):
    if os.path.isfile(lsname):
        if lsname.endswith('.net'):
            filelist.append(lsname)

aggregatelist = []
for file in filelist:
    foo = pickle.load(open("./%s" % file, 'r'))
    for entry in foo:
        if entry not in aggregatelist:
            aggregatelist.append(entry)

print 'missing pkgs:'
for file in aggregatelist:
    print file

a = open('./final-list', 'w')
pickle.dump(aggregatelist, a)
a.close()
