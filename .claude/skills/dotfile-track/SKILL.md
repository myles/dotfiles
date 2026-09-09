---
name: dotfile-track
description: Decide which layer each new or changed dotfile belongs in — ~/.dotfiles (public), ~/.dotfiles-private, or ~/.dotfiles-local — and move it there. Use after adding or editing config in this repo, especially after Claude Code has written new files, before committing anything, or when a config turns out to be machine-specific or to contain a secret.
---

# dotfile-track

`~/.dotfiles` is a **public** repo (`github.com/myles/dotfiles`). Anything written here is one `git push` from being permanently public, and the default failure mode is silent: a new config lands in whichever directory the session happened to be working in, which is almost always this one.

Run this after a batch of config changes, before the commit. The job is to place each file, not to commit it.

## The three layers

`rcrc` sets `DOTFILES_DIRS="$HOME/.dotfiles-local $HOME/.dotfiles-private $HOME/.dotfiles"`. Earlier wins.

| Layer | Versioned? | Holds |
| --- | --- | --- |
| `~/.dotfiles-local` | No — plain directory, no git, no backup | Machine-specific config: absolute paths that exist only on this Mac, per-machine overrides, anything disposable |
| `~/.dotfiles-private` | Should be a private git repo | Secrets, tokens, internal hostnames, employer- or client-specific config — things worth syncing between your own machines but never publishing |
| `~/.dotfiles` | Yes — public on GitHub | Config that is true for anyone, contains no secrets and no machine or employer specifics |

`~/.dotfiles-private` does not exist yet. If a file needs it, create it as part of the fix (step 4) rather than settling for one of the other two.

## Steps

1. List what is new or changed, across both layers that exist:

   ```
   git -C ~/.dotfiles status --short
   ls -A ~/.dotfiles-local
   ```

   Read the actual contents of every new file. Placement cannot be decided from a filename.

2. Classify each file by working down these questions and stopping at the first "yes":

   1. Does it contain a secret, token, key, password, or credential? → **private**. Never public, and never local either: local is unversioned, so a secret there is one `rm -rf` from gone.
   2. Would it be wrong or broken on another machine — absolute paths, a hostname, a serial number, hardware-specific settings? → **local**.
   3. Does it name an employer, an internal host, a client, or a private repo? → **private**.
   4. Otherwise → **public**.

   State the verdict and the reason for each file. If a single file mixes public and private content, split it: the shareable part stays public and the rest moves, rather than exiling the whole file.

3. Before anything stays in or moves to the public layer, grep it for the obvious markers and say plainly what you found:

   ```
   git -C ~/.dotfiles diff --cached -U0; git -C ~/.dotfiles diff -U0
   grep -rniE 'secret|token|passwo?rd|api[_-]?key|private[_-]key|BEGIN [A-Z ]*PRIVATE KEY|bearer|[a-z0-9._-]+@[a-z0-9.-]+\.[a-z]{2,}' <files>
   ```

   A match is a prompt to look, not proof of a leak — `gitconfig` legitimately names an email address. Report matches with the line and let the user decide.

4. Move what is misplaced. `git mv` cannot cross repository boundaries, so copy, then remove from the source:

   ```
   mkdir -p ~/.dotfiles-local/zsh/configs
   cp ~/.dotfiles/zsh/configs/foo.zsh ~/.dotfiles-local/zsh/configs/foo.zsh
   git -C ~/.dotfiles rm zsh/configs/foo.zsh
   env RCRC=$HOME/.dotfiles/rcrc rcup -K
   ```

   Keep the path *relative to the layer root* identical — `zsh/configs/foo.zsh` in every layer — because that is what makes the override resolve.

   Creating the private layer, when a file needs it:

   ```
   mkdir -p ~/.dotfiles-private && git -C ~/.dotfiles-private init
   ```

   `DOTFILES_DIRS` already lists it, so it starts taking effect as soon as it exists. Tell the user to add a **private** remote; do not add one for them.

5. To track a file that is currently only in `$HOME`, always name the destination explicitly:

   ```
   env RCRC=$HOME/.dotfiles/rcrc mkrc -d ~/.dotfiles-local ~/.somerc
   ```

   Without `-d`, `mkrc` uses the first entry in `DOTFILES_DIRS` (`~/.dotfiles-local`). That default is safe but implicit, and the whole point of this skill is choosing the layer on purpose.

6. Verify:

   ```
   env RCRC=$HOME/.dotfiles/rcrc lsrc | grep <file>
   ```

   The right-hand side must be the layer you intended. Then `zsh -n` any shell file you moved, and confirm `zsh -i -c exit` still starts silently — a moved config that fails to load is a worse outcome than a misplaced one.

7. Report what moved where, then print the commit message for the public repo's side of the change. Never commit or push, in any layer.

## Rules

- **A file in an earlier layer replaces the public one wholesale — it does not merge.** So a same-named file in `~/.dotfiles-local` silently disables the public version, and fixing the public file then does nothing. Check for an existing override with `lsrc` before editing anything in this repo, and say so when you find one.
- For a small addition, prefer the additive companions — `~/.zshrc.local`, `~/.aliases.local`, `~/.gitconfig.local`, `~/.vimrc.local` are sourced *on top of* the public config. Shadow a whole file only when you genuinely need to replace it.
- Moving a secret out of `~/.dotfiles` does not unpublish it. If it was ever committed and pushed, it is in the history and on GitHub: say so, and tell the user to rotate the credential. Do not offer to rewrite history as if that fixed it.
- `~/.dotfiles-local` has no version control. Flag anything irreplaceable that is about to live only there.
- Do not add `EXCLUDES` entries to `rcrc` to hide a file. `EXCLUDES` stops rcm linking it, but the file stays in the public repo — that is concealment, not privacy.
- rcm ignores dot-prefixed top-level entries, so `.claude/`, `.editorconfig` and friends need no handling here.
