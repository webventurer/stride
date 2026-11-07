import { deepStrictEqual } from "node:assert";
import { readdirSync, readFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const commandsDir = join(strideRoot, ".claude/commands");

const markdownFiles = readdirSync(commandsDir, { recursive: true })
  .filter((path) => path.endsWith(".md"))
  .map((path) => join(commandsDir, path));

const letteredStepHeading = /^#{1,6} (?:Step )?\d+[a-zA-Z]\b/;

describe("command step numbering", () => {
  it("never puts a letter after a step number in a heading", () => {
    const lettered = markdownFiles.flatMap((file) =>
      readFileSync(file, "utf8")
        .split("\n")
        .filter((line) => letteredStepHeading.test(line))
        .map((line) => `${relative(strideRoot, file)}: ${line}`),
    );
    deepStrictEqual(lettered, []);
  });
});
