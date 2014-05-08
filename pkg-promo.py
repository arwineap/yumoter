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
parser.add_argument('-c', '--centosversion', dest="centosVer", help="Version of centos to promote from.", metavar="centosversion", default="6.4")
parser.add_argument('-e', '--environment', dest="env", help="Environment to promote from")
parser.add_argument('-l', '--list', dest="listFlag", action="store_true", default=False, help="List repo information with environments associated with")
(options, args) = parser.parse_args()

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