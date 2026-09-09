---
name: zsh-startup
description: Diagnose slow or broken zsh startup in this dotfiles setup — measure it, profile it with zprof and xtrace, find the config file responsible, and fix it without breaking the pre/oh-my-zsh/main/post load order. Use when the shell is slow to start, a new terminal prints errors or warnings, a keybinding or completion stopped working, or the user asks what is making zsh slow.
---

# zsh startup

Measure before changing anything, find the file responsible, then fix it. Never reorder the tiers in `zshrc` to buy speed — the order is load-order-critical and documented in the repo's `CLAUDE.md`.

## Layout you are debugging

`zshrc` sources, in order: `~/.zsh/functions/*` → `configs/pre/*` → oh-my-zsh (`compinit`, `bindkey -e`) → `configs/*.zsh` (main, recursive, skipping `pre/`, `post/` and `.zwc`) → `configs/post/*` → `~/.zshrc.local` → `~/.aliases` → zsh-syntax-highlighting → zsh-autosuggestions → iTerm2 integration.

Everything under `~/.zsh/` is a symlink into `~/.dotfiles/zsh/`, so an edit is live in the next shell — no `rcup` needed unless you add or rename a file.

## Steps

1. Baseline the timing. One run is noise; take the best of five:

   ```
   for i in 1 2 3 4 5; do /usr/bin/time zsh -i -c exit; done
   ```

   Record the number. Under ~250 ms is fine, ~250–500 ms is worth trimming, over a second means one config is doing something expensive or hitting the network.

2. Baseline correctness separately: `zsh -i -c exit` must print nothing at all. Any output is a bug regardless of timing — usually a missing binary that should have been guarded with `_have`, or a completion loaded before `compinit`.

3. Profile functions with `zprof`, without editing any tracked file — use a throwaway `ZDOTDIR`:

   ```
   d=$(mktemp -d)
   printf 'zmodload zsh/zprof\nsource ~/.zshrc\nzprof\n' > "$d/.zshrc"
   ZDOTDIR="$d" zsh -i -c exit | head -40
   ```

   This ranks *functions*. It attributes almost nothing to `eval "$(tool init zsh)"` calls, which is where this setup's time actually goes.

4. Profile everything else with a timestamped xtrace, then look for the gaps between consecutive lines:

   ```
   PS4='+%D{%s.%6.} %N:%i> ' zsh -i -x -c exit 2>/tmp/zsh-trace.log
   ```

   Read `/tmp/zsh-trace.log`, diff adjacent timestamps, and report the largest jumps with the file and line that caused them. This is the step that finds the real culprit.

5. Confirm the suspect by bisecting. Move candidate files aside one at a time (`mv zsh/configs/nvm.zsh /tmp/`), re-time, then put them back. Do not leave a file moved out of the repo at the end of the session.

6. Usual suspects in this setup, in rough order of cost — check these before anything else:

   - Version-manager init in `nvm.zsh`, `pyenv.zsh`, `rbenv.zsh`, `rv.zsh`: each `eval "$(… init …)"` spawns a subshell. `nvm.sh` is the worst offender.
   - `miniconda.zsh`: conda's generated init block runs `conda shell.hook`, which is slow enough to dominate a profile on its own.
   - `java.zsh`: `/usr/libexec/java_home` calls are surprisingly expensive.
   - Double `compinit`: `pre/completion.zsh` and `post/completion.zsh` both touch completion and oh-my-zsh runs `compinit` in between. A second full `compinit` costs real time; `compinit -C` skips the security check when the dump is fresh.
   - A stale or unwritable `~/.zcompdump`, which silently forces a rebuild every shell.
   - Anything that resolves a network path at startup — a mounted share, a VPN-only host, `git` against a remote.

7. Fix in this order of preference:

   1. Guard it with `_have` so a missing binary is a no-op.
   2. Make it lazy — define a shim function that runs the real init on first use, then replaces itself.
   3. Cache the generated init to a file and source that, regenerating only when the tool's binary is newer.
   4. Only then consider dropping the config.

   Keep the file in its existing tier. If a fix seems to need moving a file between `pre/`, main and `post/`, stop and explain why — that is a load-order change, not a performance fix.

8. Verify: re-run steps 1 and 2, report the before and after numbers plainly, and confirm the shell still starts silently. If a keybinding or completion was part of the complaint, test that specific thing in a fresh interactive shell rather than assuming.

## Rules

- `shellcheck` does not understand zsh; `shellcheck zshrc` will produce noise and miss real problems. Use `zsh -n <file>` for a syntax check.
- Comment the *why* on any workaround or ordering fix. The surrounding files set that bar, and the comment is the only defence against a later tidy-up reintroducing the bug.
- Machine-specific or secret fixes belong in `~/.dotfiles-local` or `~/.dotfiles-private`, not in this public repo.
- Report timings as measured. Do not claim an improvement without a re-measured number.
