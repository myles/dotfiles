---
name: commit-message
description: Draft a commit message for the current changes, following the user's commit rules and the repository's existing convention. Use when the user asks for a commit message, says "write the commit", asks how to describe a change, or finishes work that is ready to commit.
---

# Commit message

Draft a commit message for work that is already written. Print it for the user to copy — never run `git commit`, `git add`, or `git push`.

## Steps

1. Decide what the message covers:

   - If anything is staged, describe the staged changes only: `git diff --cached`.
   - Otherwise describe the working tree: `git diff` plus any untracked files from `git status --short`.

   Say which of the two you used, so the user knows what the message claims to cover.

2. Read the actual diff, not just `--stat`. The message has to explain *why* the change exists, and that is rarely visible in a file list.

3. Check the repository's convention with `git log --oneline -20`:

   - If the history uses Conventional Commits (`feat:`, `fix:`, `docs:`), match it — the prefix and its lowercase subject win over the "capitalise the subject" rule, because consistency inside a repo matters more than a global preference. Say that you matched the repo.
   - If the history is plain prose subjects, use the user's rules as written.
   - Mixed history: follow whichever style the last ten commits favour.

4. Write the subject: imperative mood ("Fix", not "Fixed" or "Fixes"), 50 characters, 72 hard, no trailing full stop. It must complete "If applied, this commit will ___".

5. Write the body: blank line after the subject, wrapped by hand at 72 characters, explaining what changed and why. Skip the body only for changes whose subject genuinely says everything — a typo fix, a version bump.

6. Add trailers only if the repo already uses them (`git log --format=%B -20 | grep -i '^[A-Za-z-]*:'`). Do not invent `Co-Authored-By`, `Refs`, or ticket trailers that the history has never seen.

7. If the diff contains several unrelated concerns, say so and draft one message per group, naming the files in each. Do not paper over a mixed diff with a vague subject like "Various fixes".

8. Print the message in a single fenced block, ready to paste. No commentary inside the block.

## Rules

- British/Canadian spelling in the message.
- Describe what the diff does, not what the user intends to do next.
- Flag anything that looks like a secret, credential, key, or customer data in the diff before printing the message — a bad commit is hard to unpublish.
- Never stage, commit, amend, or push. Preparing the message is the whole job.
