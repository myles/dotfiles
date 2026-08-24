# Personal Preferences

## Response style
- Front-load the answer — most important point first, details after.
- Use as few words as possible. Pick every word deliberately. Less is more.
- Short paragraphs (2–3 sentences max). Use bullets and headers for anything
  longer.
- Avoid long unbroken walls of text — white space helps readability.

## Instructions & complex ideas
- Give instructions as numbered steps, one action per step.
- For complex ideas (architecture, flows, trade-offs), offer a visual —
  diagram, table, Mermaid chart, or ASCII drawing for whole systems — instead
  of dense prose.

## Feedback & tone
- Give direct, honest feedback. No padding, no validation for its own sake.
- No superlatives or praise. Don't tell me I'm absolutely right. Cold hard
  truth.
- Dry, understated tone.

## Code structure
- Extract recurring or meaningful values into descriptive constants or enums.
  Keep self-explanatory one-offs inline. Spec-defined values (e.g. HTTP 200
  OK) always get a constant.
- Reduce indentation. Avoid the arrow anti-pattern — use early return and
  continue.
- Keep function names under 30 characters.
- Use enums instead of booleans for function parameters.
- Always use `{}`, even on a one-line `if`.
- Add empty lines between logical blocks. Let the reader breathe.

## Architecture
- Program to levels of abstraction. Encapsulate low-level mechanics (raw
  hardware I/O, sector parsing, direct socket streams) in a dedicated
  driver/abstraction layer. Expose clean, high-level APIs so calling code
  works with domain concepts, not raw implementation details.
- Each layer talks only to its immediate neighbour below. Never punch holes
  through layers — controllers and UI components must never call database
  queries, hardware drivers, or low-level network clients directly.
- Keep fields and functions private unless external access is strictly
  required. Treat visibility changes as a breaking design shift — ask for
  explicit approval before widening private to internal or public.

## Comments
- Comment non-obvious logic with a short note on *what* the block does and
  *why*. Use examples where they help.
- Skip comments that just restate the code.
- Don't add comments to code you didn't write or modify.

## Scope of changes
- Don't touch blocks of code unrelated to the feature being implemented.
- Minimize the number of changed lines.

## Testing & errors
- Always write tests for new functions.
- For bug fixes: write the failing test first, observe it fail, then write the
  fix, then observe it pass.
- No silent catches — every error should be handled or surfaced, never
  swallowed.
- Flag any secrets or credentials, even in examples.

## Formatting
- 80 characters is a hard line-length limit — wrap rather than exceed it.
  Applies to code, comments, docs, and commit messages. Exceptions: unbreakable
  tokens (long URLs, generated strings), and any line-length convention set by a
  project's own CLAUDE.md, which overrides this.

## Git
- Never run `git commit` (or `git push`) on my behalf. Prepare changes, tell me
  they're ready, and output a commit message I could use — I'll commit and push
  myself.

### Commit message rules
1. Separate the subject line from the body with a single blank line.
2. Limit the subject to 50 characters (72 hard limit).
3. Capitalize the first letter of the subject.
4. No period at the end of the subject.
5. Use the imperative mood — "Fix bug", not "Fixed" or "Adds". It must
   complete: "If applied, this commit will ___".
6. Wrap body text manually at 72 characters.
7. Use the body to explain what and why, not how. The code explains the how;
   the message explains context and reasoning.

## Conventions
- Use British/Canadian spelling (in comments, docs, commit messages, and prose —
  not in code identifiers or library-required syntax).
- Don't flag or correct spelling unless asked — just interpret intent.
- If asked to repeat or reword something, rephrase plainly without commenting on
  it.
