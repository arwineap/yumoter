import json
import os
import errno
import subprocess
import sys

# should create folder structure and run rsyncs

reposbasepath = '/home/aarwine/projects/yumoter/repos'

def getConfig(jsonFile):
    fh = open(jsonFile, 'r')
    jsonOutput = fh.readlines()
    fh.close()
    return json.loads(jsonOutput[0])

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

def runrsync(rsrc, rdst, args):
    # str(rsrc), str(rdst), list(args)
    sysCall = ['rsync'] + args + [rsrc, rdst]
    print ' '.join(sysCall)
    p = subprocess.Popen(sysCall, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    for line in iter(p.stdout.readline, ""):
        sys.stdout.write(line.strip() + '\r\n')
        sys.stdout.flush()
    for line in iter(p.stderr.readline, ""):
        sys.stderr.write(line.strip() + '\r\n')
        sys.stderr.flush()
    # TODO check return status please. Stop coding like a 12 year old. 

config = getConfig('config/repos.json')

for repo in config:
    print "repo: %s" % repo
    for key in config[repo]:
        print "%s: %s" % (key, config[repo][key])
    if config[repo]['type'] == 'static':
        fullpath = "%s/%s/%s/" % (reposbasepath, config[repo]['type'], config[repo]['path'])
        print "fullpath: %s" % fullpath 
        mkdir_p(fullpath)
    elif config[repo]['type'] == 'managed':
        fullpath = "%s/%s/prd/%s" % (reposbasepath, config[repo]['type'], config[repo]['path'])
        print "fullpath prd: %s" % fullpath
        mkdir_p(fullpath)
        fullpath = "%s/%s/stg/%s" % (reposbasepath, config[repo]['type'], config[repo]['path'])
        print "fullpath stg: %s" % fullpath
        mkdir_p(fullpath)
        fullpath = "%s/%s/dev/%s" % (reposbasepath, config[repo]['type'], config[repo]['path'])
        print "fullpath dev: %s" % fullpath
        mkdir_p(fullpath)
    else:
        print 'wut'
    runrsync(config[repo]['upstream'], fullpath, ['-av', '--progress'])
    print '-------------'
