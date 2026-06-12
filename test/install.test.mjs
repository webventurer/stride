import { deepStrictEqual, strictEqual } from "node:assert";
import { describe, it } from "node:test";

function deepMerge(base, overlay) {
  for (const [key, val] of Object.entries(overlay)) {
    base[key] = mergeValue(base[key], val);
  }
  return base;
}

function mergeValue(existing, val) {
  if (isObject(existing) && isObject(val)) return deepMerge(existing, val);
  if (Array.isArray(existing) && Array.isArray(val))
    return dedupeHooks(existing, val);
  return val;
}

function isObject(v) {
  return v !== null && typeof v === "object" && !Array.isArray(v);
}

function dedupeHooks(existing, incoming) {
  for (const item of incoming) {
    const isDupe = existing.some(
      (e) => JSON.stringify(e) === JSON.stringify(item),
    );
    if (!isDupe) existing.push(item);
  }
  return existing;
}

const STRIDE_SETTINGS = {
  hooks: {
    UserPromptSubmit: [
      {
        hooks: [
          {
            type: "command",
            command:
              "$CLAUDE_PROJECT_DIR/.claude/hooks/userpromptsubmit/inject_design_principles.sh",
          },
        ],
      },
    ],
    PreToolUse: [
      {
        matcher: "Bash",
        hooks: [
          {
            type: "command",
            command:
              "$CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse/block_bare_git_commit.sh",
          },
        ],
      },
    ],
  },
  permissions: {
    deny: ["mcp__claude_ai_Linear__*"],
  },
};

function cloneConfig() {
  return JSON.parse(JSON.stringify(STRIDE_SETTINGS));
}

describe("deepMerge", () => {
  it("merges into empty settings", () => {
    const settings = {};
    deepMerge(settings, cloneConfig());

    deepStrictEqual(Object.keys(settings), ["hooks", "permissions"]);
    strictEqual(settings.hooks.UserPromptSubmit.length, 1);
    strictEqual(settings.hooks.PreToolUse.length, 1);
  });

  it("preserves existing user hooks", () => {
    const settings = {
      hooks: {
        UserPromptSubmit: [
          { hooks: [{ type: "command", command: "my_custom.sh" }] },
        ],
      },
    };
    deepMerge(settings, cloneConfig());

    strictEqual(settings.hooks.UserPromptSubmit.length, 2);
    strictEqual(
      settings.hooks.UserPromptSubmit[0].hooks[0].command,
      "my_custom.sh",
    );
  });

  it("preserves existing non-hook settings", () => {
    const settings = {
      includeCoAuthoredBy: false,
      permissions: { deny: ["Bash(rm -rf :*)"] },
    };
    deepMerge(settings, cloneConfig());

    strictEqual(settings.includeCoAuthoredBy, false);
    strictEqual(settings.hooks.PreToolUse.length, 1);
  });
});

describe("Linear MCP deny propagation", () => {
  it("adds the Linear deny to settings with no permissions", () => {
    const settings = {};
    deepMerge(settings, cloneConfig());

    deepStrictEqual(settings.permissions.deny, ["mcp__claude_ai_Linear__*"]);
  });

  it("appends the Linear deny without clobbering existing entries", () => {
    const settings = { permissions: { deny: ["Bash(rm -rf :*)"] } };
    deepMerge(settings, cloneConfig());

    deepStrictEqual(settings.permissions.deny, [
      "Bash(rm -rf :*)",
      "mcp__claude_ai_Linear__*",
    ]);
  });

  it("does not duplicate the Linear deny on re-install", () => {
    const settings = {};
    deepMerge(settings, cloneConfig());
    deepMerge(settings, cloneConfig());

    deepStrictEqual(settings.permissions.deny, ["mcp__claude_ai_Linear__*"]);
  });
});

describe("dedupeHooks", () => {
  it("does not duplicate on re-install", () => {
    const settings = {};
    deepMerge(settings, cloneConfig());
    deepMerge(settings, cloneConfig());

    strictEqual(settings.hooks.UserPromptSubmit.length, 1);
    strictEqual(settings.hooks.PreToolUse.length, 1);
  });

  it("does not duplicate after three installs", () => {
    const settings = {};
    deepMerge(settings, cloneConfig());
    deepMerge(settings, cloneConfig());
    deepMerge(settings, cloneConfig());

    strictEqual(settings.hooks.UserPromptSubmit.length, 1);
    strictEqual(settings.hooks.PreToolUse.length, 1);
  });
});
