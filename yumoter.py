import sys, os, json, errno, subprocess, yum

class yumoter:
    def __init__(self, configFile):
        self.repoConfig = self.getConfig(configFile)
        self.yb = yum.YumBase()
        self.yb.setCacheDir()

    def getConfig(self, jsonFile):
        fh = open(jsonFile, 'r')
        jsonOutput = fh.readlines()
        fh.close()
        return json.loads(jsonOutput[0])

    def mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def runrsync(self, rsrc, rdst, args):
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

    def repoSearch(self, pkgName, repos):

        pkgs = yb.pkgSack.returnNewestByNameArch(patterns=pkgName)
        for pkg in pkgs:
            print "%s: %s" % (pkg, pkg.summary)
