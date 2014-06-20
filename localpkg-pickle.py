#!/usr/bin/env python2

# Get locally installed pkgs
# query against NEW yumoter repos
# create a list of missing pkgtuples.
# write list to pickle file - `hostname.pickle`

# issues
# How will i determine if ius is needed? Skip ius for now.
# puppet - Repos are strange, ignore puppet shit.


import yum
import platform
import sys
import socket
import pickle
import os

linuxdist = platform.linux_distribution()

if linuxdist[0] != 'CentOS':
    print 'no.'
    sys.exit(1)


fullver = linuxdist[1]
majorver = fullver.split('.')[0]
dotlessver = fullver.replace('.', '')

if not os.path.isdir("/home/aarwine/tmp/pickle/%s" % fullver):
	os.mkdir("/home/aarwine/tmp/pickle/%s" % fullver)

yb = yum.YumBase()
yb.setCacheDir(yum.misc.getCacheDir())
yb.repos.disableRepo("*")

localpkgs = yb.rpmdb.returnPackages()

# epel, os, updates

yb.add_enable_repo("epel-%s" % majorver, baseurls=[str("http://yumoter.gnmedia.net/epel/%s/wildwest" % majorver)], mirrorlist=None)
yb.add_enable_repo("os-%s" % dotlessver, baseurls=[str("http://yumoter.gnmedia.net/os/%s" % fullver)], mirrorlist=None)
yb.add_enable_repo("updates-%s" % majorver, baseurls=[str("http://yumoter.gnmedia.net/updates/%s/wildwest" % majorver)], mirrorlist=None)

missingpkgs = []

for pkg in localpkgs:
	pkgresult = yb.pkgSack.searchPkgTuple(pkg.pkgtup)
	#print pkgresult
	if len(pkgresult) == 0:
		#print 'missing match:', pkg
		missingpkgs.append(pkg.pkgtup)
	elif len(pkgresult) == 1:
		pass
		#print 'match found:', pkg
	else:
		print 'odd, more than one result for:', pkg
		print pkgresult
'''
print "missing pkgs:"
for pkg in missingpkgs:
	print pkg
'''
filen = "/home/aarwine/tmp/pickle/%s/%s" % (fullver, socket.getfqdn())
foo = open(filen, 'w')
pickle.dump(missingpkgs, foo)