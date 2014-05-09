#!/usr/bin/env python2


import yumoter
import argparse
import sys

# ./pkg-promo.py -c 6.4 -e wildwest
# should also support:
# ./pkg-promo.py --list
# repoName osVer
# environments
# upstream

parser = argparse.ArgumentParser(description='Promote some packages.')
plist = parser.add_argument_group('plist')
plist.add_argument('-l', '--list', action="store_true", help="List repo information with environments associated with")
promote = parser.add_argument_group('promote')
promote.add_argument('searchpkg', help="Package to search for")
promote.add_argument('-c', '--centosversion', help="Version of centos to promote from.", metavar="centosversion", default="6.4")
promote.add_argument('-e', '--environment', help="Environment to promote from")
args = parser.parse_args()

yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')
searchString = args[0]

if options.listFlag:
	# TODO
	print "TODO"
	print "repo config dump was requested"
	sys.exit(1)

yumoter.loadRepos(options.centosVer, options.env)
searchPkgList = yumoter._returnNewestByNameArch(["openssl"])
print searchPkgList