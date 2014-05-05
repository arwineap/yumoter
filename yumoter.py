#!/usr/bin/env python2
import sys, os, json, errno, subprocess, yum

class yumoter:
    def __init__(self, configFile, repobasepath):
        self.repobasepath = repobasepath
        self.reloadConfig(configFile)
        self.yb = yum.YumBase()
        self.yb.setCacheDir()

    def reloadConfig(self, jsonFile):
        self.repoConfig = self._getConfig(jsonFile)
        self._getPaths()

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

    def _runRsync(self, rsrc, rdst, args):
        # str(rsrc), str(rdst), list(args)
        sysCall = ['rsync'] + args + [rsrc, rdst]
        print sysCall
        return
        p = subprocess.Popen(sysCall, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        for line in iter(p.stdout.readline, ""):
            sys.stdout.write(line.strip() + '\r\n')
            sys.stdout.flush()
        for line in iter(p.stderr.readline, ""):
            sys.stderr.write(line.strip() + '\r\n')
            sys.stderr.flush()
        # TODO check return status please. Stop coding like a 12 year old.

    def getDeps(self, pkgObj):
        depDicts = yb.findDeps([pkgObj])
        return depDicts

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


    def syncRepos(self):
        print 'bar'
        for repo in self.repoConfig:
            print repo
            if 'upstream' in repo:
                # This repo has an upstream, it will be synced.
                _runRsync(repo['upstream'], repo['fullpaths'][0], ['-av', '--progress'])


'''
    def repoSearch(self, pkgName, repos):

        pkgs = yb.pkgSack.returnNewestByNameArch(patterns=pkgName)
        for pkg in pkgs:
            print "%s: %s" % (pkg, pkg.summary)
'''