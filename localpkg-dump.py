#!/usr/bin/env python2

import yum
import pickle
import platform
import os


linuxdist = platform.linux_distribution()

if linuxdist[0] != 'CentOS':
    print 'no.'
    sys.exit(1)

fullver = linuxdist[1]
majorver = fullver.split('.')[0]
dotlessver = fullver.replace('.', '')

#if not os.path.isdir("/home/aarwine/tmp/pickle/%s" % fullver):
#    os.mkdir("/home/aarwine/tmp/pickle/%s" % fullver)

filename = "/home/aarwine/%s.pickle" % dotlessver

current = []
if os.path.isfile(filename):
	fh = open(filename, 'r')
	current = pickle.load(fh)
	fh.close()

yb = yum.YumBase()
yb.setCacheDir(yum.misc.getCacheDir())
yb.repos.disableRepo("*")

localpkgs = yb.rpmdb.returnPackages()

for pkg in localpkgs:
	if pkg.pkgtup not in current:
		print 'appending:', pkg.pkgtup
		current.append(pkg.pkgtup)
	else:
		print 'skipping:', pkg.pkgtup

fh = open(filename, 'w')
pickle.dump(current, fh)
fh.close()