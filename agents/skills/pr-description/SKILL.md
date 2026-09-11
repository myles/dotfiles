---
name: pr-description
description: Draft a suggested pull request title and description for the current branch, filling in the repo's pull_request_template.md if one exists and referencing an issue/ticket URL. Use when the user asks for a PR title, PR description, PR body, "write my PR", or wants to open a pull request for the work on this branch.
---

# PR title and description

Draft a PR title and body for the current branch's changes. Output them for the user to copy — never open, update, or push the PR.

## Steps

1. Find the base branch, in this order:

   - An open PR for this branch already knows its base: `gh pr view --json baseRefName,number,title`.
   - Otherwise check for a stack. Any local branch that is an ancestor of `HEAD` but not of the default branch is a candidate parent — the branch is stacked on the candidate closest to `HEAD`:

     ```
     git for-each-ref --format='%(refname:short)' refs/heads/ |
       while read -r b; do
         [ "$b" = "$(git branch --show-current)" ] && continue
         git merge-base --is-ancestor "$b" HEAD || continue
         git merge-base --is-ancestor "$b" "$default" && continue
         echo "$(git rev-list --count "$b"..HEAD) $b"
       done | sort -n | head -1
     ```

   - Otherwise `git symbolic-ref --short refs/remotes/origin/HEAD`, falling back to `main`, then `master`.

   Confirm a detected parent with the user before using it — a stale local branch can look like a parent. If the current branch *is* the base branch, say so and stop.

2. Read the changes:

   ```
   git log --reverse --format='%s%n%n%b' <base>..HEAD
   git diff --stat <base>...HEAD
   ```

   Read the actual diff for any file whose purpose is not obvious from its commit messages. The commits explain intent; the diff confirms it.

3. Look for a PR template, first match wins:

   - `.github/pull_request_template.md` (any case)
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - `PULL_REQUEST_TEMPLATE.md` or `docs/PULL_REQUEST_TEMPLATE.md`
   - `.github/PULL_REQUEST_TEMPLATE/*.md` — if there are several, ask which one to use

   Search case-insensitively, e.g. `find . -ipath '*pull_request_template*' -not -path './.git/*'`.

4. Ask for the issue/ticket URL, unless the user already supplied one as an argument to the skill. Scan the branch name and commit messages for a ticket key (`ABC-123`, `#456`, a full URL) and offer what you find as the default. Accept "none" — do not block on it, and do not invent a URL or a ticket number.

5. Write the title using the user's commit-subject rules: imperative mood, capitalised, no trailing period, 50 characters (72 hard limit). Prefix it with the ticket key only if the repo's existing PR titles do so — check with `gh pr list --limit 20 --state all` when `gh` is available.

6. Write the body:

   - **With a template:** keep every heading, comment, and checkbox exactly as written, in order. Fill in the sections you can support from the diff. Leave a section empty with a short `<!-- TODO -->` note rather than guessing. Leave checkboxes unchecked unless the diff proves the item is done.
   - **Without a template:** use `## Summary` (2–4 bullets on what and why), `## Changes` (notable files or areas), and `## Testing` (what was run, or state that nothing was).
   - Put the ticket reference where the template asks for it; otherwise on its own line at the top of the body. Use a closing keyword (`Closes <url>`) only if the change actually closes the issue.

7. Output the title on its own line, then the body in a single fenced block so it can be copied whole. Follow the user's Markdown rule: one line per paragraph, no hard wrapping.

## Rules

- When the base is not the default branch, treat the PR as stacked: describe only this branch's commits, and open the body with `Stacked on <parent branch> (#N)` so the reviewer knows which diff is theirs. Mention the parent PR's number only if `gh` found it. GitHub retargets the child at the default branch automatically when the parent merges, so do not tell the user to retarget by hand.
- Describe only what is in the diff. No speculation about follow-up work unless the user mentions it.
- Do not run `gh pr create`, `gh pr edit`, `git commit`, or `git push`. If the user wants the PR opened, they will ask.
- Flag anything in the diff that looks like a secret, credential, or customer data before printing the description.
