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

I think promotionpath should be a list. Lists are ordered, so we can define things like ["dev", "stg", "prd"] or ["wildwest", "beta", "live"]. Will also allow us to solve where to promote to using srcIndex+1.
