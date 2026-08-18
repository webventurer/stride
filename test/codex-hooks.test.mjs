import { deepStrictEqual, ok, strictEqual } from "node:assert";
import { mkdirSync, readFileSync, rmSync } from "node:fs";
import { join } from "node:path";
import { after, beforeEach, describe, it } from "node:test";
import { HOOKS_FILE, writeCodexHooks } from "../install/agents/codex/hooks.mjs";

const fixtureRoot = join("/tmp", `stride-codex-hooks-${process.pid}`);

function hooksFile() {
  return JSON.parse(readFileSync(join(fixtureRoot, HOOKS_FILE), "utf8"));
}

beforeEach(() => {
  rmSync(fixtureRoot, { recursive: true, force: true });
  mkdirSync(fixtureRoot, { recursive: true });
});
after(() => rmSync(fixtureRoot, { recursive: true, force: true }));

describe("writeCodexHooks", () => {
  it("registers both hooks under the events Codex names", () => {
    writeCodexHooks(fixtureRoot);

    deepStrictEqual(Object.keys(hooksFile().hooks).sort(), [
      "PreToolUse",
      "UserPromptSubmit",
    ]);
  });

  it("matches Bash for the commit block and nothing else", () => {
    writeCodexHooks(fixtureRoot);
    const [group] = hooksFile().hooks.PreToolUse;

    strictEqual(group.matcher, "^Bash$");
    strictEqual(group.hooks[0].type, "command");
    ok(group.hooks[0].command.endsWith("block_bare_git_commit.sh"));
  });

  it("points at the scripts by a path relative to the repo root", () => {
    writeCodexHooks(fixtureRoot);

    for (const group of Object.values(hooksFile().hooks).flat()) {
      for (const hook of group.hooks) {
        ok(
          hook.command.startsWith(".claude/hooks/"),
          `expected a repo-relative command, got ${hook.command}`,
        );
      }
    }
  });

  it("leaves UserPromptSubmit unmatched so it runs on every prompt", () => {
    writeCodexHooks(fixtureRoot);
    const [group] = hooksFile().hooks.UserPromptSubmit;

    strictEqual(group.matcher, undefined);
  });
});
