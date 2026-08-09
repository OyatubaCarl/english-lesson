# Git storage policy

This repository is the source-code and metadata record for Teacher Tacos English.

## Track in Git

- application source, scripts, configuration, lesson data, and documentation
- small canonical images that cannot be regenerated cheaply
- publication metadata and manifests that do not contain credentials

## Keep outside Git

- rendered video and audio (`mp4`, `mp3`, `wav`, and related formats)
- virtual environments, downloaded models, and dictionaries
- temporary renders, build directories, caches, and local backup copies
- tokens, credentials, private keys, and re-authentication backups

Large published media should be retained in its canonical production folder and in the selected backup storage, then delivered through YouTube, Cloudflare, or another media store. Generated assets should be recreated from the tracked scripts and metadata when practical.

Do not use `git add -f` to bypass these rules for generated media. If a large binary is genuinely canonical, decide its external storage location before committing references or manifests to Git.
