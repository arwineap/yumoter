#!/usr/bin/env python2
import sys, os, json, errno, subprocess, yum

class yumoter:
    def __init__(self, configFile, repobasepath):
        self.urlbasepath = "http://yumoter.gnmedia.net"
        self.repobasepath = repobasepath
        self.changedRepos = []
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

    def _urlToRepo(self, url):
        choppedurl = url.replace("%s/" % self.urlbasepath, '')
        for tmprepo in self.repoConfig:
            if choppedurl.startswith(self.repoConfig[tmprepo]['path']):
                return tmprepo
        print "ERROR: _urlToRepo could not evaluate which repo this url came from"
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
            print "ERROR: _urlToPromoPath was called on a repo which isn't promoted."
            sys.exit(1)
        # determine current env
        currenv = os.path.basename(os.path.dirname(choppedurl))
        newenv = self.repoConfig[repo]['promotionpath'][self.repoConfig[repo]['promotionpath'].index(currenv)+1]
        result = self._urlToPath(url.replace("/%s/" % currenv, "/%s/" % newenv ))
        return result

    def _addChangedRepo(self, repoTuple):
        # repoTuple = (repoName, envName)
        # repoTuple = ("epel-6", "wildwest")
        if len(repoTuple) != 2:
            print "ERROR: _addChangedRepo did not receive the proper repoTuple type", repoTuple
        if repoTuple[0] not in self.repoConfig.keys():
            print "ERROR: _addChangedRepo supplied a repoTuple with a non-existing repo", repoTuple
        if 'promotionpath' not in self.repoConfig[repoTuple[0]]:
            print 'ERROR: _addChangedRepo supplied a repoTuple with a non-promoting repo', repoTuple
        if repoTuple[1] not in self.repoConfig[repoTuple[0]]['promotionpath']:
            print "ERROR: _addChangedRepo was supplied a promotionpath that doesn't exist", repoTuple
        self.changedRepos.append(repoTuple)

    def _hardlink(self, src, dst):
        # src and dst are PATHS, not URLs
        srcUrl = self._pathToUrl(src)
        srcRepo = self._urlToRepo(srcUrl)
        srcEnv = self._urlToEnv(srcUrl)
        dstUrl = self._pathToUrl(dst)
        dstRepo = self._urlToRepo(dstUrl)
        dstEnv = self._urlToEnv(dstUrl)
        if os.path.exists(dst):
            print "INFO: link already exists: %s" % (dst)
            return True
        print "Linking %s -> %s" % (src, dst)
        os.link(src, dst)
        if not os.path.exists(dst):
            print "ERROR: linking failed."
            sys.exit(1)
        # Queue the link destination for createrepo
        self._addChangedRepo((dstRepo, dstEnv))
        # Ok, file is linked, now we need to do some fancy footwork.
        # The rule is, links never get removed from the first environment.
        # Links do get removed as they get promoted through further environments.
        # promotionpath = ['wildwest', 'beta', 'live']
        # link wildwest -> beta
        #   No deletions
        # link beta -> live
        #   Delete beta
        ######
        # Now that we've gathered information, let's determine if we need to
        # clean up the srcLink
        if self.repoConfig[srcRepo]['promotionpath'].index(srcEnv) != 0:
            # TODO: This block signifies repos that need to be queued for createrepo.
            print "INFO: deleting unneeded link: %s" % src
            os.remove(src)
            # We removed the rpm from the source, we need to also createrepo on it.
            self._addChangedRepo((srcRepo, srcEnv))
        return True

    def _createRepo(self, repoTuple):
        # Let's create repo metadata
        syscallStdout = []
        syscallStderr = []
        syscall = ["createrepo"]
        if self._translateToMajorVer(self.repoConfig[repoTuple[0]]['osver']) == 5:
            # centos 5 repos require this flag
            syscall.append("--checksum=sha")
        syscall.append("%s/%s/%s" % (self.repobasepath, self.repoConfig[repoTuple[0]]['path'], repoTuple[1]))
        print syscall



    def createRepos(self):
        # This method should run a createrepo on each of the entries in: self.changedRepos
        # (repoName, envName)
        for repoTuple in self.changedRepos:
            self._createRepo(repoTuple)


    def promotePkg(self, pkg):
        repo = self._urlToRepo(pkg.remote_url)
        if self._repoIsPromoted(repo):
            oldpath = self._urlToPath(pkg.remote_url)
            newpath = self._urlToPromoPath(pkg.remote_url)
            print "promoting %s -> %s" % (oldpath, newpath)
            self._hardlink(oldpath, newpath)
        else:
            print "skipping %s because it is not in a promoted repo" % pkg.name

    def promotePkgs(self, pkgList):
        for pkg in pkgList:
            self.promotePkg(pkg)


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
                    print "WARNING: found multiple suggested dependencies; defaulting to %s" % suggestedDep[0]
                    print suggestedDep
                if origPkg not in resultDict:
                    resultDict[origPkg] = []
                if suggestedDep[0] not in resultDict[origPkg]:
                    resultDict[origPkg].append(suggestedDep[0])
        return resultDict

    def getNeededDeps(self, pkgObj):
        # Sometimes you need all deps, getDeps(), sometimes you need
        # Deps that are not already satisfied, getNeededDeps()
        # This method actually just cleans the output of getDeps.
        depsDict = self.getDeps(pkgObj)
        resultDict = {}
        for pkg in depsDict:
            for dep in depsDict[pkg]:
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