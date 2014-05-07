#!/usr/bin/env python2
import sys, os, json, errno, subprocess, yum

class yumoter:
    def __init__(self, configFile, repobasepath):
        self.urlbasepath = "http://yumoter.gnmedia.net"
        self.repobasepath = repobasepath
        self.reloadConfig(configFile)
        self.yb = yum.YumBase()
        self.yb.setCacheDir(yum.misc.getCacheDir())
        self.yb.repos.disableRepo("*")

    def _getConfig(self, jsonFile):
        fh = open(jsonFile, 'r')
        jsonOutput = json.load(fh)
        fh.close()
        return jsonOutput

    def _mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def _translateToMajorVer(self, ver):
        # I: 6.4
        # O: 6
        if '.' in ver:
            ver = ver.split('.')[0]
        return ver

    def _getPaths(self):
        for repo in self.repoConfig:
            repopath = []
            # Does this repo have a path for promotion?
            if 'promotionpath' in self.repoConfig[repo]:
                for promopath in self.repoConfig[repo]['promotionpath']:
                    repopath.append("%s/%s/%s" % (self.repobasepath, self.repoConfig[repo]['path'], promopath))
            else:
                # repo does not have a path for promotion
                repopath.append("%s/%s" % (self.repobasepath, self.repoConfig[repo]['path']))
            self.repoConfig[repo]['fullpaths'] = repopath

    def _getURLs(self):
        for repo in self.repoConfig:
            repoURLs = []
            if 'promotionpath' in self.repoConfig[repo]:
                for promopath in self.repoConfig[repo]['promotionpath']:
                    repoURLs.append("%s/%s/%s" % (self.urlbasepath, self.repoConfig[repo]['path'], promopath))
            else:
                repoURLs.append("%s/%s" % (self.urlbasepath, self.repoConfig[repo]['path']))
            self.repoConfig[repo]['fullurls'] = repoURLs

    def _mkPaths(self):
        masterPathList = []
        for repo in self.repoConfig:
            if 'fullpaths' in self.repoConfig[repo]:
                for entry in self.repoConfig[repo]['fullpaths']:
                    masterPathList.append(entry)
        for entry in masterPathList:
            if not os.path.isdir(entry):
                print "creating missing dir: %s" % entry
                self._mkdir_p(entry)

    def _runRsync(self, rsrc, rdst, args):
        # str(rsrc), str(rdst), list(args)
        sysCall = ['rsync'] + args + [rsrc, rdst]
        print 'sysCall', sysCall
        rsyncStdout = []
        rsyncStderr = []
        p = subprocess.Popen(sysCall, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        for line in iter(p.stdout.readline, ""):
            stdoutLine = line.strip() + '\r\n'
            rsyncStdout.append(stdoutLine)
            sys.stdout.write(stdoutLine)
            sys.stdout.flush()
        for line in iter(p.stderr.readline, ""):
            stderrLine = line.strip() + '\r\n'
            rsyncStderr.append(stderrLine)
            sys.stderr.write(stderrLine)
            sys.stderr.flush()
        return (rsyncStdout, rsyncStderr)
        # TODO check return status please. Stop coding like a 12 year old.

    def _loadRepo(self, reponame, repo):
        print "Adding repo:", reponame, repo
        # if repo is unicode and not a string, this will silently do the wrong thing
        # and all actions against the repo will fail.
        self.yb.add_enable_repo(reponame, baseurls=[str(repo)], mirrorlist=None)

    def _returnNewestByNameArch(self, patternsList):
        pkgs = self.yb.pkgSack.returnNewestByNameArch(patterns=patternsList)
        return pkgs

    def _getDeps(self, pkgObj):
        if type(pkgObj) != list:
            pkgObj = [pkgObj]
        return self.yb.findDeps(pkgObj)

    def _urlToPath(self, url):
        return "%s%s" % (self.repobasepath, url.replace(self.urlbasepath, ''))

    def loadRepos(self, osVer, env):
        # this should load all the repos for osVer in env
        # Should use an internal method to load one repo
        # by url.
        loadrepos = []
        shortenv = self._translateToMajorVer(env)
        for repo in self.repoConfig:
            if '.' in self.repoConfig[repo]['osver']:
                # This is a repo sensative to minor versions
                if osVer == self.repoConfig[repo]['osver']:
                    loadrepos.append(repo)
            else:
                # This repo cares only about major versions
                if self._translateToMajorVer(osVer) == self.repoConfig[repo]['osver']:
                    loadrepos.append(repo)
        for repo in loadrepos:
            if len(self.repoConfig[repo]['fullurls']) == 1:
                # This repo only has one env. Repo is not promoted.
                # Load the only URL you can
                self._loadRepo(repo, self.repoConfig[repo]['fullurls'][0])
            else:
                self._loadRepo(repo, self.repoConfig[repo]['fullurls'][self.repoConfig[repo]['promotionpath'].index(env)])


    def getDeps(self, pkgObj):
        if type(pkgObj) != list:
            pkgObj = [pkgObj]
        depsDict = self._getDeps(pkgObj)
        resultDict = {}
        for origPkg in depsDict:
            for dep in depsDict[origPkg]:
                suggestedDep = self.yb.bestPackagesFromList(depsDict[origPkg][dep])
                if len(suggestedDep) > 1:
                    print "WARNING: found multiple suggested dependencies"
                    print suggestedDep
                if origPkg not in resultDict:
                    resultDict[origPkg] = []
                if suggestedDep[0] not in resultDict[origPkg]:
                    resultDict[origPkg].append(suggestedDep[0])
        return resultDict

    def syncRepos(self):
        outputList = []
        for repo in self.repoConfig:
            # Only repos with upstream set need to be synced.
            if 'upstream' in self.repoConfig[repo]:
                # If the dst dir doesn't exist, create it.
                if not os.path.isdir(self.repoConfig[repo]['fullpaths'][0]):
                    self._mkPaths()
                outputList.append(self._runRsync(self.repoConfig[repo]['upstream'], self.repoConfig[repo]['fullpaths'][0], ['-av', '--progress']))
        return outputList

    def reloadConfig(self, jsonFile):
        self.repoConfig = self._getConfig(jsonFile)
        self._getPaths()
        self._getURLs()

'''
    def repoSearch(self, pkgName, repos):

        pkgs = yb.pkgSack.returnNewestByNameArch(patterns=pkgName)
        for pkg in pkgs:
            print "%s: %s" % (pkg, pkg.summary)
'''