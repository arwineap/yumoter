import yum
import yumoter
import argparse
import sys
import os
import rpm
import platform
from pprint import pprint

import yum as yum2

# ignore list
# ['facter', 'puppet', 'puppet-server', 'ruby-augeas', 'ruby-shadow']

#     def searchExact(self, pkgName, pkgVersion, pkgRelease, pkgArch):


parser = argparse.ArgumentParser(description='Promote pkgs that are installed locally')
parser.add_argument('-e', '--environment', action='store', required=True, dest='env', help='Env to promote from')
args = parser.parse_args()

currenv = args.env

linuxdist = platform.linux_distribution()

if linuxdist[0] != 'CentOS':
    print 'no.'
    sys.exit(1)

fullver = linuxdist[1]
majorver = fullver.split('.')[0]
dotlessver = fullver.replace('.', '')

yumoterEnvs = ['wildwest', 'beta', 'live']

normalrepos = ['epel-', 'ius-', 'updates-']
otherrepos = ['os-']
loadQueue = []

yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')

yb = yum.YumBase()

yb.setCacheDir()


sysyb = yum2.YumBase()
sysyb.setCacheDir()


pkgs = yb.rpmdb.returnPackages()

for repo in normalrepos:
    loadQueue.append(repo + majorver)
for repo in otherrepos:
    loadQueue.append(repo + dotlessver)

for repo in loadQueue:
    if repo.startswith('os-'):
        yumoter._loadRepo(repo, yumoter.repoConfig[repo]['fullurls'][0])
    else:
        yumoter._loadRepo(repo, yumoter.repoConfig[repo]['fullurls'][yumoterEnvs.index(currenv)])

missingshit = []
for pkg in pkgs:
    # def searchExact(self, pkgName, pkgVersion, pkgRelease, pkgArch):
    print 'searching for:', pkg
    a = yumoter.searchPkgTuple(pkg.pkgtup)
    if len(a) == 0:
        missingshit.append(pkg)
    for result in a:
        print '  result:', result, result.remote_url
    '''
    print pkg
    print pkg.name
    print pkg.version
    print pkg.release
    print pkg.arch'''

print 'MISSING SHIT'
print missingshit
pprint(missingshit[0].__dict__)
pprint(missingshit[0].repo.__dict__)

sysyb.getReposFromConfig()

sysmissingshit = []
needpromolist = []

for pkg in missingshit:
    print 'searching missingshit:', pkg
    # yb.pkgSack.searchPkgTuple(pkgTuple)
    a = sysyb.pkgSack.searchPkgTuple(pkg.pkgtup)
    print 'a', a
    if len(a) == 0:
        sysmissingshit.append(pkg)
    for result in a:
        print 'sysresult:', result, result.remote_url
        if '/updates/' not in result.remote_url:
            if 'yum.gnmedia.net/live/puppet/' not in result.remote_url:
                needpromolist.append(result)

# If this has shit in it, check `yum list extras`
print 'unexpected extras:', sysmissingshit

promoqueue = []

print 'These pkgs are missing from new repos, and are in our current repos:'
for pkg in needpromolist:
    #print pkg, pkg.remote_url, pkg.pkgtup
    result = yumoter.searchPkgTuple(pkg.pkgtup)
    #print result
    if len(result) == 0:
        print 'NO MATCH FOUND:', pkg, pkg.remote_url
    elif len(result) == 1:
        print 'Match found, adding to queuing to promo'
        promoqueue.append(result[0])
    else:
        print 'MULTIPLE MATCHES WUT.'
        print result