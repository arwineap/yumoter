#!/usr/bin/env python2
import sys, os, json, errno, subprocess, yum

class yumoter:
    def __init__(self, configFile, repobasepath):
        self.repoConfig = self._getConfig(configFile)
        self.yb = yum.YumBase()
        self.yb.setCacheDir()
        self.repobasepath = repobasepath

    def _getConfig(self, jsonFile):
        fh = open(jsonFile, 'r')
        jsonOutput = fh.readlines()
        fh.close()
        return json.loads(jsonOutput[0])

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

    def syncRepos(self, configFile=None):
        if not configFile:
            configFile = self.repoConfig
'''
    def repoSearch(self, pkgName, repos):

        pkgs = yb.pkgSack.returnNewestByNameArch(patterns=pkgName)
        for pkg in pkgs:
            print "%s: %s" % (pkg, pkg.summary)
'''