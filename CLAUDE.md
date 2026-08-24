# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal dotfiles repo managed by [rcm](https://github.com/thoughtbot/rcm).
Every top-level file/directory is symlinked into `$HOME` with a dot prefix:
`zshrc` → `~/.zshrc`, `zsh/` → `~/.zsh/`, `bin/` → `~/.bin/`,
`config/ghostty/config` → `~/.config/ghostty/config`. Editing a file here edits
the live config — there is no build step and no test suite.

`claude/CLAUDE.md` is **not** this file: it is the user's global Claude Code
preferences, symlinked to `~/.claude/CLAUDE.md`. Changes to it take effect in
every project.

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

`rcup` has no dry-run; `lsrc` is the way to see what is linked. By default it
runs `hooks/pre-up` (installs oh-my-zsh if missing) and `hooks/post-up`
(vim-plug install/update, `/etc/zshenv` sanity check). Both hit the network, so
pass `-K` when you only want the symlinks refreshed.

## Layering: local → private → public

`rcrc` sets `DOTFILES_DIRS="$HOME/.dotfiles-local $HOME/.dotfiles-private
$HOME/.dotfiles"`. Earlier directories win, so machine-specific and secret
config lives outside this repo and overrides it. This repo is the public
fallback — keep anything sensitive out of it and expect a `.local` counterpart
to exist:

- `~/.zshrc.local`, `~/.aliases.local`, `~/.gitconfig.local`, `~/.vimrc.local`
- `~/.bin-local/` is on `PATH` ahead of most entries

## zsh load order (the part that needs explaining)

`zshrc` sources things in a deliberate sequence; getting it wrong fails
silently rather than loudly. `_load_settings` loads one *tier* of
`~/.zsh/configs` at a time:

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

- **`pre/`** is for `PATH`/`FPATH` only. `pre/homebrew.zsh` resolves
  `HOMEBREW_ROOT` from brew's canonical symlink (not `command -v brew`) because
  a poisoned `PATH` propagates into nested shells.
- **`post/`** is for keybindings and completion fixes, because oh-my-zsh's
  `bindkey -e` and fzf's widgets discard anything set earlier.
- Highlighting/autosuggestions wrap existing widgets, so they must load after
  every widget is defined.

## Conventions in this repo

- Guard optional tooling with `_have`, e.g.
  `if _have rv; then eval "$(rv shell init zsh)"; fi` — a missing binary should
  be a no-op, never a "command not found" on every prompt.
- Follow any `PATH`/`FPATH` change with `export -U PATH` to dedupe.
- Comment the *why* for ordering and workaround code; the surrounding files set
  a high bar for this and it is the main defence against someone "tidying" a
  load-order fix.
- Lines wrap at 80 characters. LF endings and a trailing newline
  (`.editorconfig`); `gitconfig` uses tabs.
- `bin/` scripts are user-facing CLIs (Python 3 with type hints, argparse,
  `--dry-run` support) and land on `PATH` via `~/.bin`.
