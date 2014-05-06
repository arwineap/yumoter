import yumoter

yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')

yumoter.loadRepos("6.4", "wildwest")
yumoter._returnNewestByNameArch(["httpd"])

#     def loadRepos(self, osVer, env):
'''
#print yumoter.repoConfig
output = yumoter.syncRepos()

print "errors:"
for entry in output:
	print entry[1]

print yumoter.repoConfig
'''