#!/usr/bin/env python2

import yum
import platform
import pickle

linuxdist = platform.linux_distribution()

if linuxdist[0] != 'CentOS':
    print 'no.'
    sys.exit(1)


fullver = linuxdist[1]
majorver = fullver.split('.')[0]
dotlessver = fullver.replace('.', '')


yb = yum.YumBase()
yb.setCacheDir(yum.misc.getCacheDir())
yb.repos.disableRepo("*")


# yb.add_enable_repo("epel-%s" % majorver, baseurls=[str("http://yumoter.gnmedia.net/epel/%s/wildwest" % majorver)], mirrorlist=None)
# pkgresult = yb.pkgSack.searchPkgTuple(pkg.pkgtup)

epelurl = "http://yum.gnmedia.net/wildwest/epel/%s/" % majorver
osurl = "http://yum.gnmedia.net/wildwest/centos/%s/os/" % fullver
updatesurl = "http://yum.gnmedia.net/wildwest/centos/%s/updates/" % fullver
iusurl = "http://yum.gnmedia.net/wildwest/ius/%s/" % majorver
gnurl = "http://yum.gnmedia.net/live/gnrepo/%s/" % majorver


loadrepos = []
loadrepos.append(("epel-repo", epelurl))
loadrepos.append(("os-repo", osurl))
loadrepos.append(("updates-repo", updatesurl))
loadrepos.append(("ius-repo", iusurl))
loadrepos.append(("gn-repo", gnurl))



for repo in loadrepos:
	yb.add_enable_repo(repo[0], baseurls=[str(repo[1])], mirrorlist=None)


filen = "./final-list"
foo = open(filen, 'r')
missingpkgs = pickle.load(foo)

for pkgtup in missingpkgs:
	result = yb.pkgSack.searchPkgTuple(pkgtup)
	if len(result) > 0:
		if len(result) == 1:
			print 'Found:', result
			print "URL: %s" % result[0].remote_url
		else:
			print 'Found multiple:', result
	else:
		print 'Still missing', pkgtup
