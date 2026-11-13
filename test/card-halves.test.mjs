import { ok } from "node:assert";
import { readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const templatesRoot = ".claude/commands/linear/reference/templates";
const readerLines = [
  "**Serves:**",
  "**Today:**",
  "**The problem:**",
  "**The change:**",
  "**Example:**",
];
const instructionFolders = [".claude/commands", ".claude/stride/docs", "docs"];

function read(path) {
  return readFileSync(join(strideRoot, path), "utf8");
}

function markdownFiles(folder) {
  return readdirSync(join(strideRoot, folder), { withFileTypes: true }).flatMap(
    (entry) => {
      const path = join(folder, entry.name);
      if (entry.isDirectory()) return markdownFiles(path);
      return entry.name.endsWith(".md") ? [path] : [];
    },
  );
}

describe("card halves", () => {
  for (const name of ["story", "bug", "epic"]) {
    const path = `${templatesRoot}/${name}.md`;

    it(`${name} template opens with the reader's half, five lines in order, a rule, then the builder's half`, () => {
      const template = read(path);
      const format = template.slice(template.indexOf("FORMAT:"));
      const positions = [
        "**For the reader**",
        ...readerLines,
        "\n---\n\n**For the builder**",
      ].map((marker) => format.indexOf(marker));

      ok(
        positions.every((position) => position >= 0),
        `${name}: a marker is missing`,
      );
      ok(
        positions.every(
          (position, i) => i === 0 || position > positions[i - 1],
        ),
        `${name}: markers are out of order`,
      );
    });

    it(`${name} template example shows the same two halves`, () => {
      const template = read(path);
      const example = template.slice(template.indexOf("## Example"));
      const positions = [
        "**For the reader**",
        ...readerLines,
        "\n---\n\n**For the builder**",
      ].map((marker) => example.indexOf(marker));

      ok(
        positions.every(
          (position, i) =>
            position >= 0 && (i === 0 || position > positions[i - 1]),
        ),
        `${name}: example is missing a marker or has them out of order`,
      );
    });

    it(`${name} template example keeps each reader's line to two sentences with no backticks`, () => {
      const template = read(path);
      const example = template.slice(template.indexOf("## Example"));
      const lines = example
        .split("\n\n")
        .filter((paragraph) =>
          /^\*\*(Today|The problem|The change|Example):\*\*/.test(paragraph),
        );

      ok(
        lines.length === 4,
        `${name}: expected four labelled lines, found ${lines.length}`,
      );
      for (const line of lines) {
        ok(
          (line.match(/[.!?](\s|$)/g) ?? []).length <= 2,
          `${name}: over two sentences: ${line}`,
        );
        ok(!line.includes("`"), `${name}: backticks in: ${line}`);
      }
    });

    it(`${name} template has no Where things stand section`, () => {
      ok(!read(path).includes("### Where things stand"), name);
    });
  }

  it("no instruction asks a card writer for a Where things stand section", () => {
    const allowed = ["older card", "There is no"];
    const offenders = instructionFolders
      .flatMap(markdownFiles)
      .flatMap((path) =>
        read(path)
          .split("\n")
          .filter((line) => line.includes("Where things stand"))
          .filter((line) => !allowed.some((phrase) => line.includes(phrase)))
          .map((line) => `${path}: ${line.slice(0, 80)}`),
      );

    ok(offenders.length === 0, offenders.join("\n"));
  });

  it("the start-check brief names all three reader's-half stops", () => {
    const brief = read(
      ".claude/commands/linear/reference/card-start-review.md",
    );
    const section = brief.slice(
      brief.indexOf("## The reader's half"),
      brief.indexOf("## The six kinds of finding"),
    );

    ok(section.includes("A promise the builder's half doesn't make"));
    ok(section.includes('A "Serves:" line that doesn\'t match the Vision'));
    ok(section.includes("A line over two sentences"));
    ok(section.includes("`contradictory` stop"));
  });

  it("every step that rewords a card rewords both halves", () => {
    for (const path of [
      ".claude/commands/linear/start.md",
      ".claude/commands/linear/reference/card-check.md",
      ".claude/commands/linear/reference/carry-lessons.md",
      ".claude/commands/linear/reference/card-language.md",
    ]) {
      ok(/both halves/.test(read(path)), path);
    }
  });
});
