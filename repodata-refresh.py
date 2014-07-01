#!/usr/bin/env python2


import yumoter

#yumoter = yumoter.yumoter('config/repos.json', '/home/aarwine/git/yumoter/repos')
yumoter = yumoter.yumoter('config/repos.json', '/mnt/yum_repos/yumoter/repos')

for reponame in yumoter.repoConfig:
	if 'promotionpath' in yumoter.repoConfig[reponame]:
		# this puppy is promoted.
		for envname in yumoter.repoConfig[reponame]['promotionpath']:
			repoTuple = (reponame, envname)
			yumoter._addChangedRepo(repoTuple)
	else:
		pass

yumoter.createRepos()
