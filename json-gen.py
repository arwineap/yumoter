import json

repos = {}
reposbasepath = '/home/aarwine/projects/yumoter/repos'

# static real path = "%s/%s/%s" % (reposbasepath, type, path)
repos['os-64'] = {}
repos['os-64']['upstream'] = 'rsync://mirrors.kernel.org/centos/6.4/os/x86_64/Packages/'
repos['os-64']['path'] = 'os/6.4'
repos['os-63'] = {}
repos['os-63']['upstream'] = 'rsync://vault.centos.org/6.3/os/x86_64/Packages/'
repos['os-63']['path'] = 'os/6.3'

repos['updates-6'] = {}
repos['updates-6']['upstream'] = 'rsync://mirrors.kernel.org/centos/6/updates/x86_64/Packages/'
repos['updates-6']['path'] = 'updates/6'
repos['updates-6']['promotionpath'] = ['wildwest', 'beta', 'live']

repos['epel-6'] = {}
repos['epel-6']['upstream'] = 'rsync://mirrors.kernel.org/fedora-epel/6/x86_64/'
repos['epel-6']['path'] = 'epel/6'
repos['epel-6']['promotionpath'] = ['wildwest', 'beta', 'live']

repos['ius-6'] = {}
repos['ius-6']['upstream'] = 'rsync://mirror.rackspace.com/ius/stable/Redhat/6/x86_64/'
repos['ius-6']['path'] = 'ius/6'
repos['ius-6']['promotionpath'] = ['wildwest', 'beta', 'live']

fh = open('config/repos.json', 'w')
fh.write(json.dumps(repos, sort_keys=True, indent=4, separators=(',', ': ')))
fh.close()
