#!/usr/bin/env python2

import yum
import yumoter
import pickle
import platform


linuxdist = platform.linux_distribution()

if linuxdist[0] != 'CentOS':
    print 'no.'
    sys.exit(1)

#fullver = linuxdist[1]
#majorver = fullver.split('.')[0]
#dotlessver = fullver.replace('.', '')

fullver = '6.5'
majorver = '6'
dotlessver = '65'

filename = "/home/aarwine/prd-final.pickle"
env = 'wildwest'

fh = open(filename, 'r')
pkgs = pickle.load(fh)
fh.close()

#yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')
yumoter = yumoter.yumoter('config/repos.json', '/mnt/yum_repos/yumoter/repos')

#loadRepos(self, osVer, env, repo)
# searchPkgTuple(self, pkgTuple)

for reponame in yumoter.repoConfig:
	if yumoter.repoConfig[reponame]['osver'] == fullver or yumoter.repoConfig[reponame]['osver'] == majorver:
		#yumoter.repoConfig[reponame]['fullurls']
		if len(yumoter.repoConfig[reponame]['fullurls']) == 1:
			yumoter._loadRepo(reponame, yumoter.repoConfig[reponame]['fullurls'][0])
		else:
			yumoter._loadRepo(reponame, yumoter.repoConfig[reponame]['fullurls'][yumoter.repoConfig[reponame]['promotionpath'].index(env)])

promocount = 0
wtdcount = 0
missingcount = 0

missingpkgs = []
wtdpkgs = []


for pkgtup in pkgs:
	result = yumoter.searchPkgTuple(pkgtup)
	if len(result) == 1:
		#print 'promoting', result[0].pkgtup
		yumoter.promotePkg(result[0])
		promocount += 1
	elif len(result) > 1:
		#print 'what to do:', result
		wtdcount += 1
		wtdpkgs.append(pkgtup)
	else:
		#print 'MISSING:', pkgtup
		missingcount += 1
		missingpkgs.append(pkgtup)

yumoter.createRepos()


for missing in missingpkgs:
	print 'missing:', missing
for wtd in wtdpkgs:
	print 'wtd:', wtd

print "---"

print "SUMMARY:"
print "promoted:", promocount
print "WTD:", wtdcount
print "missing:", missingcount



print 'writing to pickle files'

fh = open('./missingpkgs.pickle', 'w')
pickle.dump(missingpkgs, fh)
fh.close()

fh = open('./wtdpkgs.pickle', 'w')
pickle.dump(wtdpkgs, fh)
fh.close()

#depyumoter.promotePkg(pkgObj)
#depyumoter.createRepos()
