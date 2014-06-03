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
depyumoter.loadRepos(args.centosversion, environments[currEnvIdx+1], args.repo)

# load dep repos to start search for deps
#yumoter.loadRepos(args.centosversion, args.environment, args.repo)

print 'Getting deps for:', promopkg
neededDeps = depyumoter.getNeededDeps(promopkg)

depsDict = {}
for dep in neededDeps:
    depRepo = depyumoter._urlToRepo(dep.remote_url)
    if depRepo not in depsDict:
        depsDict[depRepo] = []
    depsDict[depRepo].append(dep)


'''
resultingDeps = []
tmpyumoter = yumoter.yumoter('config/repos.json', '/vagrant/yumoter/repos')



    depEnv = yumoter._urlToEnv(dep.remote_url)


tmpyumoter = yumoter.yumoter('config/repos.json', '/vagrant/yumoter/repos')
'''


'''

for dep in neededDeps[promopkg]:
    # Check all environments above the one you are in.
    # if the pkg is in an above env, remove it from neededDeps.
    # find env
    depenv = yumoter._urlToEnv(dep.remote_url)
    deprepo = yumoter._urlToRepo(dep.remote_url)
    envidx = yumoter.repoConfig[deprepo]['promotionpath'].index(depenv)+1
    for i in range(envidx, len(yumoter.repoConfig[deprepo]['promotionpath'])):
        checkenv = yumoter.repoConfig[deprepo]['promotionpath'][i]
        tmpyumoter = yumoter.yumoter('config/repos.json', '/vagrant/yumoter/repos')
        tmpyumoter.loadRepos(args.centosversion, checkenv)

#yumoter = yumoter.yumoter('config/repos.json', '/vagrant/yumoter/repos')
#yumoter.loadRepos(args.centosversion, args.environment)
#searchPkgList = yumoter._returnNewestByNameArch([args.search])

    print dep
    print yumoter._urlToPromoPath(dep.remote_url)
    print yumoter._pathToUrl(yumoter._urlToPromoPath(dep.remote_url))
    a = yumoter._urlToPromoPath(yumoter._pathToUrl(yumoter._urlToPromoPath(dep.remote_url)))
    print a
    print yumoter._pathToUrl(a)
    if not yumoter._urlToPromoPath(yumoter._pathToUrl(a)):
        print "we're done here"
    #print yumoter._urlToPromoPath(yumoter._pathToUrl(a))

print neededDeps[promopkg]

'''










'''
print("Please select which pkg to promote:")
for idx, pkg in enumerate(searchPkgList):
    print("%s: %s-%s-%s.%s" % (idx, pkg.name, pkg.version, pkg.release, pkg.arch))
pkgChoice = int(raw_input(": "))


print("Getting deps for %s-%s-%s.%s" % (searchPkgList[pkgChoice].name, searchPkgList[pkgChoice].version, searchPkgList[pkgChoice].release, searchPkgList[pkgChoice].arch))
neededDeps = yumoter.getNeededDeps(searchPkgList[pkgChoice])

for idx, dep in enumerate(neededDeps[searchPkgList[pkgChoice]]):
    print("%s: %s-%s-%s.%s" % (idx, dep.name, dep.version, dep.release, dep.arch))
promoteall = raw_input("Continue? (Y/N): ")


if promoteall.lower() == "n":
    sys.exit(0)
if promoteall.lower() != "y":
    print("invalid selection.")
    sys.exit(1)

yumoter.promotePkg(searchPkgList[pkgChoice])
yumoter.promotePkgs(neededDeps[searchPkgList[pkgChoice]])
yumoter.createRepos()

'''

