import { deepStrictEqual, ok } from "node:assert";
import { readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const commandsRoot = join(strideRoot, ".claude/commands/linear");

function read(path) {
  return readFileSync(join(commandsRoot, path), "utf8");
}

function cardTextWriters() {
  return readdirSync(commandsRoot)
    .filter((name) => name.endsWith(".md"))
    .filter((name) => {
      const command = read(name);
      return ["linear_cli.py issue create", "linear_cli.py comment create"].some(
        (write) => command.includes(write),
      );
    })
    .sort();
}

describe("Linear card language", () => {
  it("keeps clear-speak canonical without losing technical detail", () => {
    const reference = read("reference/card-language.md");

    ok(reference.includes("../../../skills/clear-speak/SKILL.md"));
    ok(
      reference.includes(
        "../../../skills/clear-speak/writing/george-orwell-rules-for-writing.md",
      ),
    );
    ok(reference.includes("filenames"));
    ok(reference.includes("constraints"));
    ok(reference.includes("edge cases"));
    ok(reference.includes("acceptance criteria"));
    ok(reference.includes("Preserve user-written text"));
  });

  it("covers every command that writes card text", () => {
    const writers = cardTextWriters();

    deepStrictEqual(writers, [
      "finish.md",
      "plan-work.md",
      "quick.md",
      "setup.md",
    ]);
    for (const name of writers) {
      ok(read(name).includes("reference/card-language.md"), name);
    }
  });
});
