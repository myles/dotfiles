# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal dotfiles repo managed by [rcm](https://github.com/thoughtbot/rcm). Every top-level file/directory is symlinked into `$HOME` with a dot prefix: `zshrc` → `~/.zshrc`, `zsh/` → `~/.zsh/`, `bin/` → `~/.bin/`, `config/ghostty/config` → `~/.config/ghostty/config`. Editing a file here edits the live config — there is no build step and no test suite.

`.claude/skills/*/SKILL.md` are skills scoped to *this* repo — they only load when Claude Code is run from inside it, and they need no `rcup`. rcm ignores dot-prefixed top-level entries, so nothing under `.claude/` is ever symlinked into `$HOME`. Put a skill here when it is only useful against these dotfiles, and in `agents/skills/` when it is useful everywhere.

## Shared agent config: agents/ → claude/ + codex/

Claude Code and Codex read the same global instructions and the same personal skills. `agents/` is the single source of truth; the per-harness directories hold nothing but symlinks into it:

```
agents/AGENTS.md                     ← the user's global preferences
agents/skills/<name>/SKILL.md        ← personal skills, harness-agnostic
claude/CLAUDE.md              -> ../agents/AGENTS.md          → ~/.claude/CLAUDE.md
claude/skills/<name>          -> ../../agents/skills/<name>   → ~/.claude/skills/<name>/
codex/AGENTS.md               -> ../agents/AGENTS.md          → ~/.codex/AGENTS.md
codex/skills/<name>           -> ../../agents/skills/<name>   → ~/.codex/skills/<name>/
```

- `agents/` is in `EXCLUDES` so rcm does not also link it to a pointless `~/.agents/`. The symlinks still resolve — the filesystem follows them, rcm does not.
- rcm descends *through* an in-repo symlinked directory: it creates a real directory in `$HOME` and symlinks each leaf file, so `~/.claude/skills/foo/SKILL.md` reaches the canonical file in two hops. That is the shape `~/.claude/skills/` is in, and Claude Code reads it fine.
- **That two-hop shape does not work for Codex.** Codex skips a skill directory whose `SKILL.md` is a symlink — the skill simply never appears in its list, with no warning. It *does* follow a symlinked skill *directory*. So `rcrc` sets `SYMLINK_DIRS="codex/skills/*"`, which tells rcm to symlink each skill directory rather than descend into it. `SKILL.md` is then a real file at the end of the chain and Codex sees it. If a Codex skill goes missing, the fix is `rcup` — not editing `~/.codex/` by hand.
- **`SYMLINK_DIRS` is the fix here, not a `post-up` hook, and reverting it corrupts the repo.** `post-up` used to relink `~/.codex/skills/<name>` after rcm built it. On the *next* `rcup`, rcm walked `codex/skills/<name>/SKILL.md`, followed that new link back into the repo, found the canonical file at the destination, and replaced `agents/skills/<name>/SKILL.md` with a symlink to itself — `ELOOP`, both harnesses lose the skill, and a later `rcup` does not repair it. Any scheme where a hook rewrites what rcm just built has this shape. Keep the linking inside rcm's own config.
- `SYMLINK_DIRS` applies only to `codex/skills/*`. `~/.codex/skills/` also holds directories this repo does not own (Codex's own, plugins, project-scoped links); symlinking the whole `codex/skills` directory would hide them.
- **Adding a shared skill:** create it under `agents/skills/`, then add one symlink per harness. Both are needed — nothing is discovered automatically.
- **Harness-only skill:** put a real directory in `claude/skills/` or `codex/skills/` instead. That is the whole reason these are per-skill symlinks and not one symlink for the entire `skills/` directory.
- `agents/AGENTS.md` is **not** this file: it is the user's global preferences, and a change to it takes effect in every project, in both harnesses. Keep it harness-agnostic — do not mention Claude-specific or Codex-specific tooling in it.

## Commands

| Task | Command |
| --- | --- |
| Link/refresh all dotfiles | `env RCRC=$HOME/.dotfiles/rcrc rcup` |
| Link, skipping the hooks | `env RCRC=$HOME/.dotfiles/rcrc rcup -K` |
| List managed symlinks | `env RCRC=$HOME/.dotfiles/rcrc lsrc` |
| Track a new file in the repo | `mkrc ~/.somerc` |
| Verify a shell change | `zsh -i -c exit` (must print nothing) |
| Time shell startup | `time zsh -i -c exit` |
| Lint a shell file | `shellcheck zshrc` |
| Run the commit guards over everything | `pre-commit run --all-files` |
| Test the commit guard | `python3 .pre-commit-hooks/test_check_forbidden.py` |

`rcup` has no dry-run; `lsrc` is the way to see what is linked. By default it runs `hooks/pre-up` (installs oh-my-zsh if missing) and `hooks/post-up` (vim-plug install/update, `pre-commit install`, `/etc/zshenv` sanity check). Both hit the network, so pass `-K` when you only want the symlinks refreshed.

## Layering: local → private → public

`rcrc` sets `DOTFILES_DIRS="$HOME/.dotfiles-local $HOME/.dotfiles-private $HOME/.dotfiles"`. Earlier directories win, so machine-specific and secret config lives outside this repo and overrides it. This repo is the public fallback — keep anything sensitive out of it and expect a `.local` counterpart to exist:

- `~/.zshrc.local`, `~/.aliases.local`, `~/.gitconfig.local`, `~/.vimrc.local`
- `~/.bin-local/` is on `PATH` ahead of most entries

## Commit guards (pre-commit)

This repo is public, so `.pre-commit-config.yaml` refuses any commit carrying credentials, internal hostnames, SSH config for real infrastructure, or employer references. Three hooks run: `detect-private-key`, `detect-secrets`, and the local `.pre-commit-hooks/check_forbidden.py`.

`pre-commit install` wires it into `.git/hooks`. `hooks/post-up` does that on every `rcup` and warns loudly when `pre-commit` is not installed — an unguarded clone is the failure mode that matters.

The employer-specific strings are deliberately **not** in this repo: a denylist published alongside the thing it protects announces exactly what it is hiding. They live in `~/.dotfiles-private/.pre-commit-denylist.txt` — one entry per line, either a literal (matched whole-word, case-insensitively) or a `/regex/`, with `#` comments — and `$DOTFILES_DENYLIST` overrides the path. The leading dot keeps rcm from symlinking it into `$HOME`. Add new strings there, never here.

- A missing, unreadable, or empty denylist is a hard failure (exit 2), not a skip. A guard that quietly disables itself is worse than none, because you stop checking by hand.
- False positive: put `allow-forbidden` in a comment on the line, or `pragma: allowlist secret` for detect-secrets.
- The scanner and its tests exclude themselves from the scan — they contain the patterns and sample keys on purpose.
- The generic rules live in the script because none of them are sensitive: RFC 1918 addresses, `.internal`/`.corp`/`.lan`/`.consul` hostnames, `ProxyJump`/`IdentityFile` directives, and vendor key shapes. Note that `.local` is *not* a flagged suffix — this repo's whole layering convention depends on it.
- Tests are stdlib `unittest`, so they run before anything is installed. Add a case for every rule you add.

## zsh load order (the part that needs explaining)

`zshrc` sources things in a deliberate sequence; getting it wrong fails silently rather than loudly. `_load_settings` loads one *tier* of `~/.zsh/configs` at a time:

```
zsh/functions/*        →  helpers like _have, mcd, ips
configs/pre/*          →  PATH + FPATH that everything downstream needs
oh-my-zsh              →  runs compinit, forces `bindkey -e`
configs/*.zsh (main)   →  per-tool init: pyenv, rbenv, nvm, go, rust, fzf, …
configs/post/*         →  anything that must beat oh-my-zsh/fzf
~/.zshrc.local, ~/.aliases
zsh-syntax-highlighting, zsh-autosuggestions  →  always last
```

Rules that fall out of this:

- **`pre/`** is for `PATH`/`FPATH` only. `pre/homebrew.zsh` resolves `HOMEBREW_ROOT` from brew's canonical symlink (not `command -v brew`) because a poisoned `PATH` propagates into nested shells.
- **`post/`** is for keybindings and completion fixes, because oh-my-zsh's `bindkey -e` and fzf's widgets discard anything set earlier.
- Highlighting/autosuggestions wrap existing widgets, so they must load after every widget is defined.

## Conventions in this repo

- Guard optional tooling with `_have`, e.g. `if _have rv; then eval "$(rv shell init zsh)"; fi` — a missing binary should be a no-op, never a "command not found" on every prompt.
- Follow any `PATH`/`FPATH` change with `export -U PATH` to dedupe.
- Comment the *why* for ordering and workaround code; the surrounding files set a high bar for this and it is the main defence against someone "tidying" a load-order fix.
- Code and comments wrap at 80 characters; Markdown is left unwrapped, one line per paragraph. LF endings and a trailing newline (`.editorconfig`); `gitconfig` uses tabs.
- `bin/` scripts are user-facing CLIs and land on `PATH` via `~/.bin`. Python 3 (type hints, argparse) is the default; bash is fine for thin wrappers around another CLI, with `set -euo pipefail` and a hand-rolled arg loop. Either way: a usage comment at the top, `--help`, `--dry-run`, and a non-zero exit distinguishing a bad invocation from a failure in the underlying tool.
