import { deepStrictEqual, strictEqual } from "node:assert";
import { execFileSync } from "node:child_process";
import { describe, it } from "node:test";
import { deepMerge, STRIDE_SETTINGS } from "../bin/install.mjs";

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

describe("direct-execution guard", () => {
  it("importing the module does not run the installer", () => {
    const moduleUrl = new URL("../bin/install.mjs", import.meta.url).href;
    const output = execFileSync(
      process.execPath,
      ["--input-type=module", "-e", `import ${JSON.stringify(moduleUrl)}`],
      { encoding: "utf8", timeout: 10000 },
    );

    strictEqual(output, "");
  });
});
