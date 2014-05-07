import yumoter

yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')

yumoter.loadRepos("6.4", "wildwest")
a = yumoter._returnNewestByNameArch(["openssl"])
a = a[0]
print a
print a.name
print a.arch
print a.epoch
print a.version
print a.release
print a.size

b = yumoter.getDeps(a)

print "###"

print b
'''
print "deps:"
for pkg in b:
	print pkg.name, pkg.arch, pkg.version
'''



#     def loadRepos(self, osVer, env):
'''
#print yumoter.repoConfig
output = yumoter.syncRepos()

print "errors:"
for entry in output:
	print entry[1]

print yumoter.repoConfig
'''