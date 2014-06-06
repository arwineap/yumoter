import yum
import yumoter
import argparse
import sys
import os
import rpm
import platform
from pprint import pprint


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

# Figure out repos to load
for repo in normalrepos:
    loadQueue.append(repo + majorver)
for repo in otherrepos:
    loadQueue.append(repo + dotlessver)

# Load repos
for repo in loadQueue:
    if repo.startswith('os-'):
        yumoter._loadRepo(repo+"yumoter", yumoter.repoConfig[repo]['fullurls'][0])
    else:
        yumoter._loadRepo(repo+"yumoter", yumoter.repoConfig[repo]['fullurls'][yumoterEnvs.index(currenv)])


missingshit = []
promoqueue = []

# Iterate through all installed pkgs, search through yumoter for
# matching pkgs.
pkgs = yb.rpmdb.returnPackages()
for pkg in pkgs:
    # def searchExact(self, pkgName, pkgVersion, pkgRelease, pkgArch):
    #print 'searching for:', pkg
    a = yumoter.searchPkgTuple(pkg.pkgtup)
    if len(a) == 0:
        missingshit.append(pkg)
    elif len(a) == 1:
        #print '  perfect match:', a[0], a[0].remote_url
        promoqueue.append(a[0])
    else:
        print '  muliple matches:'
        for idx, entry in enumerate(a):
            print "    %s. %s" % (idx, entry)
        print 'this was really unexpected, stopping.'
        sys.exit(1)

# missingshit are rpmdb pkgobjects from installed pkgs that are not in yumoter.
# promoqueue is a list of yumoter pkgs we matched from locally installed pkgs


print "#### MISSINGSHIT ####"
for entry in missingshit:
    # facter is handled by puppet repos which are not dealt with here. We will set them up by hand
    if entry.name != 'facter':
        # Puppet repos are not dealt with here.
        if entry.name != 'puppet':
            # c6.5 has newer git than our custom one (not sure where it came from)
            if entry.name != 'git':
                # c6.5 has newer git than our custom one (not sure where it came from)
                if entry.name != 'perl-Git':
                    print entry




# Let's clean the promoqueue, it doesn't need pkgs from os repos
removequeue = []
for entry in promoqueue:
    if yumoter._urlToRepo(entry.remote_url).startswith('os-'):
        removequeue.append(entry)
for entry in removequeue:
    promoqueue.remove(entry)

print "#### PROMOQUEUE ####"
for entry in promoqueue:
    print entry

