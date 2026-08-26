import { ok } from "node:assert";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

function read(path) {
  return readFileSync(join(strideRoot, path), "utf8");
}

describe("config defaults", () => {
  it("has check report and offer to write a missing default", () => {
    const check = read(".claude/commands/linear/check.md");

    ok(check.includes("backfill-focus"));
    ok(check.includes("backfill-unattended"));
    ok(check.includes("Add them now? (y/n)"));
    ok(check.includes("Unattended mode writes the missing defaults"));
  });

  it("keeps setup the author and check the repairer", () => {
    const setup = read(".claude/commands/linear/setup.md");

    ok(setup.includes("single place config defaults are *authored*"));
    ok(setup.includes("may repair a config that predates a field"));
  });

  it("names the repair offer in the unattended contract", () => {
    const policy = read(".claude/commands/linear/reference/unattended.md");

    ok(policy.includes("`/linear:check` reports the field"));
  });
});
