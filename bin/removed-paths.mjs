// Paths the installer shipped before and no longer delivers; on re-run it
// offers to remove any still present. When you drop or rename a shipped file,
// add its old path here — the install-prune test fails if an entry is still
// shipped.
export const REMOVED_PATHS = [
  ".claude/tools/linear_client.py", // dropped (WB-443)
  ".claude/tools/openrouter-chat.py", // renamed to openrouter_cli.py (WB-278)
  ".claude/docs/concepts/atomicity.md", // docs relocated to .claude/stride/docs/
  ".claude/docs/patterns/git/atomic-git-commits.md",
  ".claude/docs/principles/design-decisions.md",
  ".claude/docs/principles/single-responsibility-principle.md",
  ".claude/commands/linear/reference/BUG-TEMPLATE.md", // renamed to templates/bug.md (WB-469)
  ".claude/commands/linear/reference/EPIC-TEMPLATE.md", // renamed to templates/epic.md (WB-469)
  ".claude/commands/linear/reference/ISSUE-TEMPLATE.md", // renamed to templates/issue.md (WB-469)
];
