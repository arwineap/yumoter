#!/usr/bin/env python2

import yum
import yumoter
import argparse
import sys
import os

import yumoter as depyumoter


def commonInLists(listOfLists):
    # Input: List of lists
    # Output: Single list of common elements
    # Must take unknown number of lists
    if len(listOfLists) == 0:
        raise Exception('No.')
    elif len(listOfLists) == 1:
        return listOfLists[0]
    elif len(listOfLists) == 2:
        return list(set(listOfLists[0]).intersection(listOfLists[1]))
    elif len(listOfLists) > 2:
        result = set(listOfLists[0]).intersection(listOfLists[1])
        for i in range(2, len(listOfLists)):
            result = result.intersection(listOfLists[i])
        return list(result)
    else:
        raise Exception('How did I get here?')


parser = argparse.ArgumentParser(description='The yumoter promo script will assist you in promoting pkgs and their dependencies through environments.',
                                epilog="Example: ./pkg-promo.py search -c 6.5 -e wildwest -r epel-6 GitPython")

subparsers = parser.add_subparsers(help='Use search to promote something, and list to get information about the repos', dest='subprocess_name')

parser_list = subparsers.add_parser('list', help='List repo information')

parser_search = subparsers.add_parser('search', help='Search for pkgs')
parser_search.add_argument('search', help='specify a pkg to search for')
parser_search.add_argument('-c', '--centosversion', help="Specify centos version", default="6.4")
parser_search.add_argument('-e', '--environment', help="Specify enviornment / promotion path", required=True)
parser_search.add_argument('-r', '--repo', help="Repo to search in", required=True)

args = parser.parse_args()

environments = ['wildwest', 'beta', 'live']

#yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')
yumoter = yumoter.yumoter('/mnt/yum_repos/yumoter/config/repos.json', '/mnt/yum_repos/yumoter/repos')
#yumoter = yumoter.yumoter('config/repos.json', '/vagrant/yumoter/repos')

if args.subprocess_name == 'list':
    for repo in yumoter.repoConfig:
        print(repo)
        for key in yumoter.repoConfig[repo]:
            if isinstance(yumoter.repoConfig[repo][key], basestring):
                print("  %s: %s" % (key, yumoter.repoConfig[repo][key]))
            else:
                print("  %s:" % key)
                for entry in yumoter.repoConfig[repo][key]:
                    print("    %s" % entry)
    sys.exit()

# Load initial repo to do search
if len(yumoter.repoConfig[args.repo]['fullurls']) == 1:
    yumoter._loadRepo(args.repo, yumoter.repoConfig[args.repo]['fullurls'][0])
else:
    yumoter._loadRepo("%s-%s" % (args.repo, args.environment), yumoter.repoConfig[args.repo]['fullurls'][yumoter.repoConfig[args.repo]['promotionpath'].index(args.environment)])

searchPkgList = yumoter.searchByName(args.search)

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
#print pkgIdx[160]
#promopkg = pkgIdx[160]


currEnvIdx = environments.index(args.environment)

# setup depyumoter
depyumoter = depyumoter.yumoter('/mnt/yum_repos/yumoter/config/repos.json', '/mnt/yum_repos/yumoter/repos')
depyumoter.loadRepos(args.centosversion, args.environment, args.repo)

# get initial deps for our chosen pkg
print 'Getting deps for:', promopkg
neededDeps = depyumoter.getNeededDeps(promopkg)

# Put the chosen pkg in a list with it's deps
depsList = [promopkg]

# If the pkg has no deps, don't try to iterate through them.
if len(neededDeps) != 0:
    for dep in neededDeps[promopkg]:
        depsList.append(dep)


depNameDict = {}
# Get full list of dependencies
fullDepResult = depyumoter._getDeps(depsList)

commonPkgDict = {}
for pkg in fullDepResult:
    for dep in fullDepResult[pkg]:
        if dep[0] not in commonPkgDict:
            commonPkgDict[dep[0]] = []
        commonPkgDict[dep[0]].append(fullDepResult[pkg][dep])

for key in commonPkgDict:
    commonPkgDict[key] = commonInLists(commonPkgDict[key])

promoList = [promopkg]

for key in commonPkgDict:
    choicepkg = depyumoter.yb.bestPackagesFromList(commonPkgDict[key])
    for entry in choicepkg:
        if depyumoter._repoIsPromoted(depyumoter._urlToRepo(entry.remote_url)):
            if entry not in promoList:
                promoList.append(entry)

print ""
print "Promotion list:"
goprettydict = {}
for idx, entry in enumerate(promoList):
    repoName = yumoter._urlToRepo(entry.remote_url)
    if repoName not in goprettydict:
        goprettydict[repoName] = []
    goprettydict[repoName].append(entry)

for repo in goprettydict:
    print "%s" % repo
    for pkg in goprettydict[repo]:
        print "  %s" % pkg

goVar = raw_input("Go? (y|n): ")

if goVar.lower() == 'n':
    sys.exit(0)
elif goVar.lower() == 'y':
    for pkg in promoList:
        depyumoter.promotePkg(pkg)
else:
    print 'wut.'

print "creating repos"
depyumoter.createRepos()
