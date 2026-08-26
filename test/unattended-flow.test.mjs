import { ok } from "node:assert";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";
import { linearCommandNames } from "../install/linear-commands.mjs";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

function read(path) {
  return readFileSync(join(strideRoot, path), "utf8");
}

describe("unattended Linear flow", () => {
  it("gives every command the shared unattended contract", () => {
    for (const name of linearCommandNames(strideRoot)) {
      const command = read(`.claude/commands/linear/${name}.md`);
      ok(command.includes("reference/unattended.md"), name);
    }
  });

  it("defaults to interactive and preserves hard stops", () => {
    const policy = read(".claude/commands/linear/reference/unattended.md");
    ok(policy.includes(".unattended // false"));
    ok(policy.includes("Failed validation"));
    ok(policy.includes("Unsafe repository state"));
    ok(policy.includes("Ambiguous"));
    ok(policy.includes("tracked `.stride.json`"));
  });

  it("removes routine delivery pauses", () => {
    const start = read(".claude/commands/linear/start.md");
    const quick = read(".claude/commands/linear/quick.md");
    const epic = read(
      ".claude/commands/linear/reference/epic-iteration.md",
    );
    ok(start.includes("then run `/linear:finish`"));
    ok(quick.includes("does not require a ship phrase"));
    ok(quick.includes("Do not launch diffity"));
    ok(epic.includes("continue to the next unfinished"));
  });

  it("keeps ambiguous choices out of unattended mode", () => {
    const plan = read(".claude/commands/linear/plan-work.md");
    const finish = read(".claude/commands/linear/finish.md");
    const next = read(".claude/commands/linear/next-steps.md");
    const setup = read(".claude/commands/linear/setup.md");
    const vision = read(".claude/commands/linear/update-vision.md");
    ok(plan.includes("scope shape is not safe to guess"));
    ok(next.includes("a read-only command\nnever starts mutating work"));
    ok(setup.includes("stops rather than guessing"));
    ok(vision.includes("immediately in unattended mode"));
  });

  it("handles stretched Vision matches by mode", () => {
    for (const name of ["quick", "finish"]) {
      const command = read(`.claude/commands/linear/${name}.md`);
      ok(command.includes("Update an existing Success criterion"), name);
      ok(command.includes("add a new Success criterion"), name);
      ok(command.includes("Interactive mode stops"), name);
      ok(command.includes("In unattended mode, add a new Success criterion"), name);
      ok(command.includes("separate atomic commit"), name);
      ok(command.includes("continue without asking"), name);
    }

    const quick = read(".claude/commands/linear/quick.md");
    ok(!quick.includes("Ship anyway against that criterion"));

    const policy = read(".claude/commands/linear/reference/unattended.md");
    ok(policy.includes("Vision fit follows the delivery command"));
  });

  it("materialises the default in new configs", () => {
    for (const path of [
      ".claude/commands/linear/plan-work.md",
      ".claude/commands/linear/next-steps.md",
      ".claude/commands/linear/reference/create-project.md",
      ".claude/commands/linear/reference/setup.md",
    ]) {
      ok(read(path).includes('"unattended": false'), path);
    }
  });
});
