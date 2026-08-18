// Paths the installer shipped before and no longer delivers; on re-run it
// offers to remove any still present. When you drop or rename a shipped file,
// add its old path here — the install-prune test fails if an entry is still
// shipped.

export const REMOVED_PATHS = [
  ".claude/tools/linear_client.py",
  ".claude/tools/openrouter-chat.py",
  ".claude/docs/concepts/atomicity.md",
  ".claude/docs/patterns/git/atomic-git-commits.md",
  ".claude/docs/principles/design-decisions.md",
  ".claude/docs/principles/single-responsibility-principle.md",
  ".claude/commands/linear/reference/BUG-TEMPLATE.md",
  ".claude/commands/linear/reference/EPIC-TEMPLATE.md",
  ".claude/commands/linear/reference/ISSUE-TEMPLATE.md",
];
