---
name: review-changes
description: Work out what should be reviewed from the current git state — uncommitted work, the branch, or the whole repository — estimate what the review will cost in tokens, money, and time, then run it once approved. Use when the user asks for a code review, says "review this", "review my branch", "review the repo", or wants to know what a review will cost before starting it.
---

# Review changes

Decide what to review, say what it will cost, get approval, then review. This skill owns scope and cost — it does not replace the review itself. A whole-repository review of a large project costs a hundred times what a branch diff costs, and the point of the estimate is that the user finds that out before paying for it, not after.

## Choosing the target

Top-down, first match wins.

| Git state | Target | Scope |
| --- | --- | --- |
| Working tree is dirty | Uncommitted work | Staged + unstaged + untracked |
| Clean, on a non-default branch | The branch | `<remote>/<default>...HEAD` |
| Clean, on the default branch | **Ask first** | The whole repository |
| Clean, detached HEAD | Offer `<remote>/<default>...HEAD`, else ask | — |
| No commits yet | Untracked files; stop if the tree is empty | Working tree |
| Not a git repository | Stop and say so | — |

Dirty beats everything, so on the default branch with uncommitted changes you review the changes and never ask. Always say which row you took.

## Steps

1. Establish the repository state. Run the repo check first — every other probe lies outside a repository.

   ```sh
   git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit   # not a repo
   git rev-parse --verify -q HEAD >/dev/null 2>&1                # false => no commits
   [ -z "$(git branch --show-current)" ]                         # true  => detached HEAD
   [ -n "$(git status --porcelain --untracked-files=all | head -1)" ]   # => dirty
   ```

   Test for zero commits *before* detached HEAD. Do not use `git rev-parse --abbrev-ref HEAD`: it prints `HEAD` for both an unborn branch and a detached one, and writes a fatal to stderr on a repository with no commits. `git branch --show-current` returns the unborn branch name and is empty only when genuinely detached, which makes it the only reliable discriminator.

2. Resolve the default branch. Try these in order, and if none of them resolves, do not guess `main` — skip the branch row and ask instead.

   ```sh
   base=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
   [ -n "$base" ] || for b in main master trunk develop; do
     git show-ref --verify -q "refs/heads/$b" && { base=$b; break; }
   done
   [ -n "$base" ] || base=$(git config --get init.defaultBranch 2>/dev/null)
   ```

   The default branch is whatever this reports, even when it is neither `main` nor `master` — plenty of repositories default to `staging` or `develop`, and a hardcoded pair silently reviews the wrong range.

3. Prefer the remote-tracking ref over the local branch, and `upstream` over `origin` when both exist. On a fork, `origin/HEAD` points at the fork, whose default branch trails the real base.

   ```sh
   : "${base:?no default branch resolved - ask, do not diff}"
   for r in upstream origin; do
     git show-ref --verify -q "refs/remotes/$r/$base" && { ref="$r/$base"; break; }
   done
   : "${ref:=$base}"
   ```

   A stale local default branch overstates the range by an order of magnitude, so this is not cosmetic. Use three dots: two-dot folds the default branch's own commits into the diff as reversals. Print the ref you chose so the user can override it.

   Do not let `ref` reach step 4 empty. `"$ref...HEAD"` with an empty `ref` expands to `...HEAD`, which git reads as `HEAD...HEAD`: zero bytes, **exit 0**, nothing on stderr to catch. The skill then quotes the floor price for a branch of any size and reviews nothing, which is indistinguishable from an honest empty diff. Bail to the ask instead.

4. Measure the target in bytes and files, capturing both into variables step 6 reads. Anchor at the repository root first — `git ls-files` emits repo-relative paths, but `xargs cat` resolves them against the shell's working directory.

   **Run steps 4 to 6 in one shell invocation.** Most harnesses give each command its own shell, so `base`, `ref`, `BYTES` and `FILES` do not survive between tool calls. Assigning them in one call and reading them in the next leaves them empty, and step 6 silently prices the empty string as zero — see the warning there.

   ```sh
   cd "$(git rev-parse --show-toplevel)"
   EMPTY_TREE=4b825dc642cb6eb9a060e54bf8d69288fbee4904   # git hash-object -t tree /dev/null

   # (a) Uncommitted: tracked delta plus untracked text files
   BYTES=$({ git diff HEAD 2>/dev/null || git diff "$EMPTY_TREE" 2>/dev/null
     git ls-files -o --exclude-standard -z | xargs -0 grep -Il . --null 2>/dev/null \
       | xargs -0 cat 2>/dev/null
   } | wc -c)
   FILES=$({ git diff --name-only HEAD 2>/dev/null
     git ls-files -o --exclude-standard; } | sort -u | wc -l)
   MULT=2.5

   # (b) Branch
   BYTES=$(git diff --no-ext-diff "$ref...HEAD" 2>/dev/null | wc -c)
   FILES=$(git diff --numstat "$ref...HEAD" 2>/dev/null | wc -l)
   MULT=2.5

   # (c) Whole repository: tracked, text, non-generated
   git grep -I --name-only -e '' -z -- \
     ':!:*.lock' ':!:*-lock.json' ':!:pnpm-lock.yaml' ':!:go.sum' \
     ':!:*.min.js' ':!:*.min.css' ':!:*.map' ':!:*.snap' ':!:*.svg' \
     ':!:*.generated.*' ':!:*_pb2.py' ':!:*.pb.go' ':!:*.pot' ':!:*.po' \
     ':(glob,exclude)**/node_modules/**' ':(glob,exclude)**/vendor/**' \
     ':(glob,exclude)**/third_party/**' ':(glob,exclude)**/.venv/**' \
     ':(glob,exclude)**/dist/**' ':(glob,exclude)**/build/**' \
     ':(glob,exclude)**/target/**' ':(glob,exclude)**/__generated__/**' \
     2>/dev/null > /tmp/review-files.z
   BYTES=$(xargs -0 cat < /tmp/review-files.z 2>/dev/null | wc -c)
   FILES=$(tr -dc '\0' < /tmp/review-files.z | wc -c)
   MULT=1.15
   ```

   `git grep -I --name-only -e ''` is the load-bearing part: plain git, no `file(1)`, and it drops binaries *and* symlinks in one pass. Without it, a tracked symlink is counted twice — once as the link, once through its target.

   Directory excludes need `:(glob,exclude)**/dir/**`, not `:!:dir/**`. Plain `:!:` anchors at the repository root, so in a monorepo every nested `vendor/`, `dist/`, `build/` and `target/` is counted and reviewed. Prefixing `**/` without the `:(glob)` magic is worse than leaving it alone: it picks up the nested copies but stops matching the top-level one. Extension patterns like `:!:*.min.js` already match at any depth and are left as they are.

   Four things are not optional. Redirect stderr everywhere, or a `fatal:` gets counted as review content. Use NUL delimiters with `xargs -0` throughout, or a tracked path containing a space breaks the pipeline. Spell it `grep -Il . --null`, not `-Z`: on BSD grep, as shipped with macOS, `-Z` is not `--null` and emits newlines, which silently reintroduces the bug for any path containing one. Pass `--exclude-standard` when listing untracked files, which is the difference between zero bytes and several hundred megabytes of build output.

5. Sanity-check the count before estimating. `--exclude-standard` is necessary but not sufficient: an untracked directory that was never gitignored — a `build/`, a virtualenv — still lands in the total. Count files first, and if untracked files dominate, name the offenders with `git ls-files -o --exclude-standard --directory` and offer to gitignore them rather than review them.

6. Estimate. `mult` is `2.5` for a diff, because the review reads the surrounding code and not only the hunks, and `1.15` for a whole repository, where the files already *are* the context.

   ```sh
   : "${BYTES:?step 4 did not run in this shell}"
   : "${FILES:?step 4 did not run in this shell}"
   : "${MULT:?pick 2.5 for a diff, 1.15 for a whole repository}"

   awk -v bytes="$BYTES" -v files="$FILES" -v mult="$MULT" 'BEGIN {
     BYTES_PER_TOKEN    = 4        # rough ratio for source code
     TOKENS_PER_FILE    = 1200     # reading 50 files costs more than their diff suggests
     MIN_INPUT_TOKENS   = 15000    # harness floor: system prompt, skill text, tool schemas
     OUTPUT_RATIO       = 0.15     # a review reads a lot and writes little
     MIN_OUTPUT_TOKENS  = 2000
     MAX_OUTPUT_TOKENS  = 40000    # review output is bounded by human attention
     CONTEXT_TOKENS     = 200000   # past this the review needs another pass
     IN_USD_PER_MTOK    = 5.00     # list rate, input
     OUT_USD_PER_MTOK   = 25.00    # list rate, output
     OUT_TOKENS_PER_MIN = 4000     # wall clock tracks generation, not prefill

     input = bytes / BYTES_PER_TOKEN * mult
     if (files * TOKENS_PER_FILE > input) input = files * TOKENS_PER_FILE
     if (input < MIN_INPUT_TOKENS)        input = MIN_INPUT_TOKENS
     passes = int(input / CONTEXT_TOKENS) + 1
     input += (passes - 1) * MIN_INPUT_TOKENS        # each pass re-pays the floor
     output = input * OUTPUT_RATIO
     if (output < MIN_OUTPUT_TOKENS) output = MIN_OUTPUT_TOKENS
     if (output > MAX_OUTPUT_TOKENS) output = MAX_OUTPUT_TOKENS
     usd  = input/1e6*IN_USD_PER_MTOK + output/1e6*OUT_USD_PER_MTOK
     mins = 0.5 + output/OUT_TOKENS_PER_MIN + passes*0.5
     printf "%d in / %d out tokens, %d pass(es), ~$%.2f, %.0f-%.0f min\n",
       input, output, passes, usd, mins/2, mins*2
   }'
   ```

   The `:?` guards are the point of this block, not decoration. awk coerces an unset variable to `0`, so an empty `BYTES` does not fail — it sends `input` down to `MIN_INPUT_TOKENS` and quotes a whole-repository review of a large project at one pass and a few cents. That is precisely the surprise this skill exists to prevent, arriving with a confident number attached. Fail loudly instead.

   The floors matter more than the ceilings: on a three-line diff the real cost is almost entirely harness overhead, so an estimate without `MIN_INPUT_TOKENS` is wrong by two orders of magnitude.

7. Print the target, the ref it came from, the byte and file counts, and the estimate — then ask to proceed. Every time, for every target. When the estimate is large, lead with the pass count rather than the money: "this needs 98 passes" ends the conversation where a dollar figure invites haggling.

8. On approval, hand the resolved target to the harness's code-review tooling, passing the target explicitly so it cannot re-derive a different scope, and forwarding any effort level the user asked for. If the harness has no review tooling, review inline: correctness bugs first, then reuse and simplification, reporting each finding as `file:line`, one sentence naming the defect, and a concrete failure scenario. Say which of the two paths you took.

   Search adversarially, report neutrally. Go in assuming the change is broken and that the author was wrong about something, because the default failure of a review is agreement rather than harshness. Do not carry that assumption into the verdict: a finding needs concrete inputs or state that produce a wrong result, and whatever cannot be stated that way is not a finding. "No defects found" remains a legal outcome. Aiming to reject trades a false-negative problem for a false-positive one, which is the worse of the two — a confident invented defect costs more to disprove than a missed one costs to catch later.

## Rules

- Never `git commit`, `git add`, `git stash`, or `git push`. Resolving scope must not touch the tree — in particular, never stash to get a clean diff.
- Never skip the approval step, however small the target. An unasked-for review is the failure this skill exists to prevent.
- State the target and its ref before the estimate. A precise estimate for the wrong scope is worse than no estimate.
- A submodule shows up as one dirty entry and a pointer change. Report `submodule <x> moved <old> → <new>, not reviewed`, and never recurse into it without asking.
- A missing `origin/HEAD` happens after `clone --single-branch` even when a remote exists. Suggest `git remote set-head origin -a`; do not run it, because it hits the network.
- The rates are list prices and ignore prompt caching, so a second review in the same session costs less than quoted. The constants are calibration, not measurement — say the estimate is order-of-magnitude, and say the time range is the least reliable of the three figures.
- Flag anything resembling a secret, credential, or customer data the moment you see it in the target, ahead of every other finding.
- Never pad a review to justify what it cost. Quoting a price first makes a clean result feel like money wasted, and that pressure is this skill's own doing — a review that found nothing and says so is the estimate being spent correctly.
