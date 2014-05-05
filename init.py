import yumoter

yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')
#print yumoter.repoConfig
output = yumoter.syncRepos()

print "errors:"
for entry in output:
	print entry[1]