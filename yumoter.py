#!/usr/bin/env python2
import sys
import os
import json
import errno
import subprocess
import yum


class yumoter:

    def __init__(self, configFile, repobasepath):
        self.urlbasepath = "http://yumoter.gnmedia.net"
        self.repobasepath = repobasepath
        self.changedRepos = []
        self.reloadConfig(configFile)
        self.yb = yum.YumBase()
        self.yb.setCacheDir(yum.misc.getCacheDir())
        self.yb.repos.disableRepo("*")
        os.umask(0o002)

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
        # ------
        # I: 6
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
                print("creating missing dir: %s" % entry)
                self._mkdir_p(entry)

    def _runRsync(self, rsyncName, rsrc, rdst, args):
        # str(rsrc), str(rdst), list(args)
        sysCall = ['rsync'] + args + [rsrc, rdst]
        rsyncStdout = []
        rsyncStderr = []
        p = subprocess.Popen(sysCall, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        for line in iter(p.stdout.readline, ""):
            stdoutLine = line.strip() + '\r\n'
            rsyncStdout.append(stdoutLine.strip())
            sys.stdout.write(stdoutLine)
            sys.stdout.flush()
        for line in iter(p.stderr.readline, ""):
            stderrLine = line.strip() + '\r\n'
            rsyncStderr.append(stderrLine.strip())
            sys.stderr.write(stderrLine)
            sys.stderr.flush()
        return (rsyncName, rsyncStdout, rsyncStderr)
        # TODO check return status please. Stop coding like a 12 year old.

    def _loadRepo(self, reponame, repo):
        print("Adding repo: %s %s" % (reponame, repo))
        # if repo is unicode and not a string, this will silently do the wrong
        # thing and all actions against the repo will fail.
        self.yb.add_enable_repo(reponame, baseurls=[str(repo)], mirrorlist=None)

    def _returnNewestByNameArch(self, patternsList):
        pkgs = self.yb.pkgSack.returnNewestByNameArch(patterns=patternsList)
        return pkgs

    def _getDeps(self, pkgObj):
        if type(pkgObj) != list:
            pkgObj = [pkgObj]
        result = self.yb.findDeps(pkgObj)
        return result

    def _urlToPath(self, url):
        return "%s%s" % (self.repobasepath, url.replace(self.urlbasepath, ''))

    def _urlToRepo(self, url):
        choppedurl = url.replace("%s/" % self.urlbasepath, '')
        for tmprepo in self.repoConfig:
            if choppedurl.startswith(self.repoConfig[tmprepo]['path']):
                return tmprepo
        print("ERROR: _urlToRepo could not evaluate which repo this url came from")
        sys.exit(1)

    def _pathToUrl(self, path):
        return "%s/%s" % (self.urlbasepath, path.replace("%s/" % self.repobasepath, ''))

    def _repoIsPromoted(self, repo):
        if 'promotionpath' not in self.repoConfig[repo].keys():
            return False
        return True

    def _urlToEnv(self, url):
        choppedurl = url.replace("%s/" % self.urlbasepath, '')
        resultenv = os.path.basename(os.path.dirname(choppedurl))
        return resultenv

    def _urlToPromoPath(self, url):
        # takes a url of an rpm
        # returns path of promoted dir
        # url = 'http://yumoter.gnmedia.net/epel/6/wildwest/tmux-1.6-3.el6.x86_64.rpm'
        repo = self._urlToRepo(url)
        choppedurl = url.replace("%s/" % self.urlbasepath, '')
        # choppedurl = epel/6/wildwest/tmux-1.6-3.el6.x86_64.rpm
        # check to see if this repo is even promoted
        if not self._repoIsPromoted(repo):
            print("ERROR: _urlToPromoPath was called on a repo which isn't promoted.")
            sys.exit(1)
        # determine current env
        currenv = os.path.basename(os.path.dirname(choppedurl))
        try:
            newenv = self.repoConfig[repo]['promotionpath'][self.repoConfig[repo]['promotionpath'].index(currenv)+1]
        except IndexError:
            return False
        result = self._urlToPath(url.replace("/%s/" % currenv, "/%s/" % newenv ))
        return result

    def _addChangedRepo(self, repoTuple):
        # repoTuple = (repoName, envName)
        # repoTuple = ("epel-6", "wildwest")
        if len(repoTuple) != 2:
            print("ERROR: _addChangedRepo did not receive the proper repoTuple type", repoTuple)
        if repoTuple[0] not in self.repoConfig.keys():
            print("ERROR: _addChangedRepo supplied a repoTuple with a non-existing repo", repoTuple)
        if 'promotionpath' not in self.repoConfig[repoTuple[0]]:
            print('ERROR: _addChangedRepo supplied a repoTuple with a non-promoting repo', repoTuple)
        if repoTuple[1] not in self.repoConfig[repoTuple[0]]['promotionpath']:
            print("ERROR: _addChangedRepo was supplied a promotionpath that doesn't exist", repoTuple)
        if repoTuple not in self.changedRepos:
            self.changedRepos.append(repoTuple)

    def _hardlink(self, src, dst):
        os.link(src, dst)
        if os.path.exists(dst):
            return True
        return False

    def _magicTranslator(self, name, version):
        majorVer = self._translateToMajorVer(version)
        dotlessVer = version.replace('.', '')
        guessedName = "%s-%s" % (name, majorVer)
        if guessedName in self.repoConfig:
            return guessedName
        guessedName = "%s-%s" % (name, dotlessVer)
        if guessedName in self.repoConfig:
            return guessedName


    def _createRepo(self, repoTuple):
        # Let's create repo metadata
        syscallStdout = []
        syscallStderr = []
        syscall = ["createrepo"]
        if self._translateToMajorVer(self.repoConfig[repoTuple[0]]['osver']) == 5:
            # centos 5 repos require this flag
            syscall.append("--checksum=sha")
        syscall.append("%s/%s/%s" % (self.repobasepath, self.repoConfig[repoTuple[0]]['path'], repoTuple[1]))
        print("Generating metadata on: %s %s" % (repoTuple[0], repoTuple[1]))
        p = subprocess.Popen(syscall, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        for line in iter(p.stdout.readline, ""):
            stdoutLine = line.strip() + '\r\n'
            syscallStdout.append(stdoutLine)
            sys.stdout.write(stdoutLine)
            sys.stdout.flush()
        for line in iter(p.stderr.readline, ""):
            stderrLine = line.strip() + '\r\n'
            syscallStderr.append(stderrLine)
            sys.stderr.write(stderrLine)
            sys.stderr.flush()
        return (syscallStdout, syscallStderr)

    def searchByName(self, pkgname):
        result = self.yb.searchGenerator(['name'], [pkgname])
        return result

    def searchPkgTuple(self, pkgTuple):
        # pkgSack.searchPkgTuple(
        result = self.yb.pkgSack.searchPkgTuple(pkgTuple)
        return result

    def createRepos(self):
        # This method should run a createrepo on each of the entries in: self.changedRepos
        # (repoName, envName)
        for repoTuple in self.changedRepos:
            self._createRepo(repoTuple)

    def promotePkg(self, pkg):
        repo = self._urlToRepo(pkg.remote_url)
        cleanuplist = []
        if self._repoIsPromoted(repo):
            oldpath = self._urlToPath(pkg.remote_url)
            newpath = self._urlToPromoPath(pkg.remote_url)
            if os.path.exists(newpath):
                print("INFO: link already exists: %s" % (newpath))
                cleanuplist.append(oldpath)
            else:
                dstUrl = self._pathToUrl(newpath)
                dstRepo = self._urlToRepo(dstUrl)
                dstEnv = self._urlToEnv(dstUrl)
                srcUrl = self._pathToUrl(oldpath)
                srcRepo = self._urlToRepo(srcUrl)
                srcEnv = self._urlToEnv(srcUrl)
                if self._hardlink(oldpath, newpath):
                    print("Linked %s -> %s" % (oldpath, newpath))
                    self._addChangedRepo((dstRepo, dstEnv))
                    cleanuplist.append(oldpath)
                else:
                    print("ERROR: link failed: %s -> %s" % (oldpath, newpath))
            for dpkg in cleanuplist:
                # Deletions should happen post-promotes if the link src is not the first
                # environment in the promopath
                # promotionpath = ['wildwest', 'beta', 'live']
                # link wildwest -> beta
                #   No deletions
                # link beta -> live
                #   Delete beta
                dUrl = self._pathToUrl(dpkg)
                dRepo = self._urlToRepo(dUrl)
                dEnv = self._urlToEnv(dUrl)
                if self.repoConfig[dRepo]['promotionpath'].index(dEnv) != 0:
                    print("INFO: deleting unneeded link: %s" % dpkg)
                    os.remove(dpkg)
                    self._addChangedRepo((dRepo, dEnv))
        else:
            print("skipping %s because it is not in a promoted repo" % pkg.name)

    def promotePkgs(self, pkgList):
        for pkg in pkgList:
            self.promotePkg(pkg)

    def loadRepos(self, osVer, env, repo):
        # this should load all the repos for osVer in env
        # Should use an internal method to load one repo
        # by url.
        loadrepos = [repo]
        for deprepo in self.repoConfig[repo]['deprepos']:
            loadrepos.append(self._magicTranslator(deprepo, osVer))
        for repo in loadrepos:
            try:
                if len(self.repoConfig[repo]['fullurls']) == 1:
                    # This repo only has one env. Repo is not promoted.
                    # Load the only URL you can
                    self._loadRepo(repo, self.repoConfig[repo]['fullurls'][0])
                else:
                    self._loadRepo("%s-%s" % (repo, env), self.repoConfig[repo]['fullurls'][self.repoConfig[repo]['promotionpath'].index(env)])
            except yum.Errors.DuplicateRepoError:
                print "Already added:", repo

    def getDeps(self, pkgObj):
        if type(pkgObj) != list:
            pkgObj = [pkgObj]
        depsDict = self._getDeps(pkgObj)
        #print 'DEBUG getDeps:', depsDict
        resultDict = {}
        for origPkg in depsDict:
            for dep in depsDict[origPkg]:
                #print 'DEBUG getDeps:', depsDict[origPkg][dep]
                suggestedDep = self.yb.bestPackagesFromList(depsDict[origPkg][dep])
                if origPkg not in resultDict:
                    resultDict[origPkg] = []
                for suggDep in suggestedDep:
                    if suggDep not in resultDict[origPkg]:
                        resultDict[origPkg].append(suggDep)
        return resultDict

    def getNeededDeps(self, pkgObj):
        # Sometimes you need all deps, getDeps(), sometimes you need
        # Deps that are not already satisfied, getNeededDeps()
        # This method actually just cleans the output of getDeps.
        depsDict = self.getDeps(pkgObj)
        resultDict = {}
        for pkg in depsDict:
            for dep in depsDict[pkg]:
                # Take out deps from repos that are not promoted. These do not
                # need to be promoted.
                if self._repoIsPromoted(self._urlToRepo(dep.remote_url)):
                    if pkg not in resultDict:
                        resultDict[pkg] = []
                    resultDict[pkg].append(dep)
        return resultDict

    def syncRepos(self):
        outputList = []
        for repo in self.repoConfig:
            # Only repos with upstream set need to be synced.
            if 'upstream' in self.repoConfig[repo]:
                # If the dst dir doesn't exist, create it.
                if not os.path.isdir(self.repoConfig[repo]['fullpaths'][0]):
                    self._mkPaths()
                outputList.append(self._runRsync(repo, self.repoConfig[repo]['upstream'], self.repoConfig[repo]['fullpaths'][0], ['-av', '--partial']))
        return outputList

    def reloadConfig(self, jsonFile):
        self.repoConfig = self._getConfig(jsonFile)
        self._getPaths()
        self._getURLs()
