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

parser = argparse.ArgumentParser(description='The yumoter promo script will assist you in promoting pkgs and their dependencies through environments.')

subparsers = parser.add_subparsers(help='sub-command help', dest='subprocess_name')

parser_list = subparsers.add_parser('list', help='list crap out')
parser_list.add_argument('--verbose', action="store_true", default=False, help="List out full repo config details")

parser_search = subparsers.add_parser('search', help='search for pkgs')
parser_search.add_argument('search', help='specify a pkg to search for')
parser_search.add_argument('-c', '--centosversion', help="Specify centos version", default="6.4")
parser_search.add_argument('-e', '--environment', help="Specify enviornment / promotion path", required=True)

args = parser.parse_args()


yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')

if args.subprocess_name == 'list':
    # TODO
    print "TODO"
    print "repo config dump was requested"
    sys.exit(1)

yumoter.loadRepos(args.centosversion, args.environment)
searchPkgList = yumoter._returnNewestByNameArch([args.search])
print searchPkgList