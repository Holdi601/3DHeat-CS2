
# Updates

3DHeat CS2 keeps itself current from this repository's
[GitHub releases](https://github.com/Holdi601/3DHeat-CS2/releases). Code:
[`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-CS2/blob/main/heat3d_update/__main__.py).

## The check at start-up

Every `python -m heat3d_cs2 ...` first asks whether a newer release is out,
before it even reads its arguments:

1. The installed version is the file `VERSION` in the repository's root
   (`0` if it cannot be read).
2. The newest release is asked of
   `https://api.github.com/repos/Holdi601/3DHeat-CS2/releases/latest`, with a
   **5 second** timeout. The answer is cached for **6 hours** in
   `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-CS2.json` (on systems without
   `LOCALAPPDATA`: `~/.cache/3DHeat/update-check-3DHeat-CS2.json`), so the
   request is made at most every six hours. "Nothing released yet" (HTTP 404)
   is cached like an answer. Offline, rate-limited, behind a proxy - any other
   failure - the tool carries on with the version it has, and nothing is
   cached.
3. Versions are compared as numbers: `v1.2.3` and `1.2.3` are equal, anything
   after a `-` or `+` is ignored, missing parts count as 0.

When a newer release is out, it says so on the error stream:

```text
[heat3d_cs2] 3DHeat CS2 1.1.0 is out (this is 1.0.1). https://github.com/Holdi601/3DHeat-CS2/releases/tag/v1.1.0
Update now? [Y/n]
```

- At a terminal (both the input and the error stream are terminals) it asks.
  Enter, `y`, `yes`, `j` or `ja` updates; anything else carries on unchanged.
  After an update **the same command runs again**, on the new code.
- Without a terminal - a scheduled run, a pipe - it only prints where to
  update and carries on: `Run python -m heat3d_update in <folder> to update.`

`HEAT3D_NO_UPDATE=1` switches the check off. Any value other than empty,
`0`, `false` or `no` counts as on.

## Updating on request

```bash
python -m heat3d_update            # update to the newest release
python -m heat3d_update --check    # only say whether one is out
```

This always asks GitHub (the cache is not used). It prints `Up to date: <version>.`,
`No release found (this is <version>); offline, or nothing published yet.`, or
`<new> is out (this is <current>): <url>` and then updates (unless `--check`).
Exit code `1` when an update was attempted and failed, `0` otherwise.

## How an update is applied

It depends on how the copy was installed:

- **A git checkout** (there is a `.git` in the root and `git` on `PATH`):
  `git pull --ff-only`. It is refused while tracked files have local changes
  ("this checkout has local changes; commit or stash them, then run
  `git pull`"): those are someone's work, and an update does not decide what
  happens to them. Untracked files do not block it.
- **A downloaded copy**: the release's source archive (GitHub's zipball) is
  downloaded and unpacked to a temporary folder - entries that would land
  outside it are skipped - and its `VERSION` must be the version the release
  claims, or nothing is changed ("the archive is version X, not Y"). Then its
  files are copied over the folder. Files that are not part of the release -
  your demos, outputs, virtual environment, anything you made - are never
  touched. Python modules that the release no longer has are deleted from the
  tool's own packages (the `heat3d_*` folders), so a stale module cannot
  shadow its replacement.

If an update fails, the message is printed and the tool runs on the version
it has.
