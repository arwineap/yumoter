import yumoter

yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')

yumoter.loadRepos("6.4", "wildwest")
a = yumoter._returnNewestByNameArch(["openssl"])
a = a[0]
print a
print "name", a.name
print "arch", a.arch
print "epoch", a.epoch
print "version", a.version
print "release", a.release
print "size", a.size
print "remote_url", a.remote_url

print yumoter._urlToPath(a.remote_url)
print yumoter._urlToPromoPath(a.remote_url)

b = yumoter.getDeps(a)

print "###"

for pkg in b:
	print pkg
	for dep in b[pkg]:
		print "\t%s - %s" % (dep, dep.remote_url)
