#!/usr/bin/env python2

import yum
import yumoter
import argparse
import sys
import os

import yumoter as depyumoter


parser = argparse.ArgumentParser(description='The yumoter promo script will assist you in promoting pkgs and their dependencies through environments.')

subparsers = parser.add_subparsers(help='Use search to promote something, and list to get information about the repos', dest='subprocess_name')

parser_list = subparsers.add_parser('list', help='List repo information')

parser_search = subparsers.add_parser('search', help='Search for pkgs')
parser_search.add_argument('search', help='specify a pkg to search for')
parser_search.add_argument('-c', '--centosversion', help="Specify centos version", default="6.4")
parser_search.add_argument('-e', '--environment', help="Specify enviornment / promotion path", required=True)
parser_search.add_argument('-r', '--repo', help="Repo to search in", required=True)

args = parser.parse_args()

environments = ['wildwest', 'beta', 'live']

yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')
#yumoter = yumoter.yumoter('config/repos.json', '/vagrant/yumoter/repos')

if args.subprocess_name == 'list':
    for repo in yumoter.repoConfig:
        print(repo)
        for key in yumoter.repoConfig[repo]:
            if isinstance(yumoter.repoConfig[repo][key], basestring):
                print("\t%s: %s" % (key, yumoter.repoConfig[repo][key]))
            else:
                print("\t%s:" % key)
                for entry in yumoter.repoConfig[repo][key]:
                    print("\t\t%s" % entry)
    sys.exit()

# Load initial repo to do search
if len(yumoter.repoConfig[args.repo]['fullurls']) == 1:
    yumoter._loadRepo(args.repo, yumoter.repoConfig[args.repo]['fullurls'][0])
else:
    yumoter._loadRepo(args.repo, yumoter.repoConfig[args.repo]['fullurls'][yumoter.repoConfig[args.repo]['promotionpath'].index(args.environment)])

#searchPkgList = yumoter._returnNewestByNameArch([args.search])
searchPkgList = yumoter.searchByName(args.search)

# searchByName doesn't return the same format as returnNewestByNameArch
# Let's fix the printing
searchPkgDict = {}

for pkg in searchPkgList:
    # Need to filter out installed pkgs. Not sure where they are coming from.
    if 'rpmdb' not in pkg[0].__dict__:
        if yumoter._urlToRepo(pkg[0].remote_url) not in searchPkgDict:
            searchPkgDict[yumoter._urlToRepo(pkg[0].remote_url)] = []
        searchPkgDict[yumoter._urlToRepo(pkg[0].remote_url)].append(pkg[0])

pkgIdx = []
i = 0
for repo in searchPkgDict:
    print("%s:" % repo)
    for pkg in searchPkgDict[repo]:
        print("%d. %s" % (i, pkg))
        pkgIdx.append(pkg)
        i += 1
print('Please select which pkg to promote:')
pkgChoice = int(raw_input(": "))

print pkgIdx[pkgChoice]
promopkg = pkgIdx[pkgChoice]
#print pkgIdx[6]
#promopkg = pkgIdx[6]


currEnvIdx = environments.index(args.environment)

# setup depyumoter
depyumoter = depyumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')
depyumoter.loadRepos(args.centosversion, args.environment, args.repo)

# load dep repos to start search for deps
#yumoter.loadRepos(args.centosversion, args.environment, args.repo)

print 'Getting deps for:', promopkg
neededDeps = depyumoter.getNeededDeps(promopkg)

depsDict = {}
for dep in neededDeps[promopkg]:
    depRepo = depyumoter._urlToRepo(dep.remote_url)
    if depRepo not in depsDict:
        depsDict[depRepo] = []
    depsDict[depRepo].append(dep)

# Let's make passes of recursive dep resolution.
changedFlag = False
while changedFlag == False:
    oldDepsDict = depsDict
    for repo in depsDict:
        for dep in depsDict[repo]:
            newdeplist = depyumoter.getNeededDeps(dep)
            print 'DEBUG newdeplist:', newdeplist
            for pkg in newdeplist:
                print 'DEBUG recursive dep', pkg
                tmprepo = yumoter._urlToRepo(pkg.remote_url)
                if tmprepo not in depsDict:
                    depsDict[tmprepo] = []
                if pkg not in depsDict[tmprepo]:
                    depsDict[tmprepo].append(pkg)
    if depsDict == oldDepsDict:
        changedFlag = True



print "Deps:"
for repo in depsDict:
    print "Repo: %s" % repo
    for dep in depsDict[repo]:
        print "\t%s" % dep


