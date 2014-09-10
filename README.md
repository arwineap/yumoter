Introduction
============
This is the in progress yumoter suite. This suite should ease the pain of syncing, managing and testing rpms / repos.

- JSON config files
- Repo sync script with email updates
- RPM configurable promotion dev->stg->prd? wildwest->beta->live?
- Promotion will do auto dependency resolution

`This document, and the code are still a work in progress`

Config file format
============
We think that all we need to define a repo is three parameters.
- localpath (req)
- upstreamurl (opt)
- promotionpath (opt)

if no upstreamurl: We are authoritative. No syncs.
if no promotionpath: static repo, doesn't change.

---
path     = epel/6
upstream      = rsync://mirrors.kernel.org/fedora-epel/6/x86_64/
promotionpath = ['wildwest', 'beta', 'live']

basepath + / + path + / + promotionpath[i]

---
path     = gnrepo/6
promotionpath = ['wildwest', 'beta', 'live']

basepath + / + path + / + promotionpath[i]

---
path = os/6.5
upstream  = rsync://mirrors.kernel.org/centos/6.4/os/x86_64/Packages/

basepath + / + path

---

I think promotionpath should be a list. Lists are ordered, so we can define things like ["dev", "stg", "prd"] or ["wildwest", "beta", "live"]. Will also allow us to solve where to promote to using srcIndex+1.

TODO / Known Issues
============
promotionpath should be configured per instance. We can't realistically support different numbers of environments per repo.

repo-sync needs to createrepo after it syncs. This is required for two reasons. First, some repos do not come down with repodata (IE jenkins), second, we are not using --delete flag on rsync, therefore our repodata is different than upstreams.
