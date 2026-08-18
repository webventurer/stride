// Registers stride's hooks with Codex. Both scripts run unchanged under either
// tool, so this writes only the wiring — Codex spawns command hooks from the
// project root, which is why the commands are repo-relative rather than
// carrying the $CLAUDE_PROJECT_DIR that Claude's own config uses.

import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";

export const HOOKS_FILE = ".codex/hooks.json";

const HOOKS = {
  PreToolUse: [
    {
      matcher: "^Bash$",
      hooks: [
        {
          type: "command",
          command: ".claude/hooks/pretooluse/block_bare_git_commit.sh",
        },
      ],
    },
  ],
  UserPromptSubmit: [
    {
      hooks: [
        {
          type: "command",
          command: ".claude/hooks/userpromptsubmit/inject_design_principles.sh",
        },
      ],
    },
  ],
};

export function writeCodexHooks(repoRoot) {
  const path = join(repoRoot, HOOKS_FILE);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(
    path,
    `${JSON.stringify({ description: "stride guardrails", hooks: HOOKS }, null, 2)}\n`,
  );
}
