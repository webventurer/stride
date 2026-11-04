import { deepStrictEqual } from "node:assert";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const strideRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const shellFences = new Set(["", "bash", "sh"]);
const logicPatterns = [
  /^\s*(then|do|else|fi|done|esac)\s*(;.*)?$/,
  /;\s*(then|do)\b/,
  /^\s*case\s.+\sin\s*$/,
  /(\|\||&&)\s*(exit|return)\b/,
  /\bpython3?\s+-c\b/,
  /\bnode\s+-e\b/,
];

function trackedCommandFiles() {
  return execFileSync("git", ["ls-files", ".claude/commands"], {
    cwd: strideRoot,
    encoding: "utf8",
  })
    .split("\n")
    .filter((path) => path.endsWith(".md"));
}

function codeOnly(line) {
  return line.replace(/'[^']*'|"[^"]*"/g, "''").replace(/(^|\s)#.*$/, "");
}

function logicLines(markdown) {
  const found = [];
  let fence = null;
  markdown.split("\n").forEach((line, index) => {
    const opener = line.match(/^\s*```(\S*)/);
    if (opener) {
      fence = fence === null ? opener[1] : null;
      return;
    }
    const isLogic = logicPatterns.some((pattern) =>
      pattern.test(codeOnly(line)),
    );
    if (shellFences.has(fence) && isLogic) found.push(index + 1);
  });
  return found;
}

describe("command files keep logic out of markdown", () => {
  it("no tracked command file has a shell block holding logic", () => {
    const offenders = trackedCommandFiles().flatMap((path) =>
      logicLines(readFileSync(join(strideRoot, path), "utf8")).map(
        (line) => `${path}:${line}`,
      ),
    );

    deepStrictEqual(offenders, []);
  });

  it("flags branches, loops, exit checks and inline code", () => {
    const block = [
      "```bash",
      'if [ -e "$f" ]; then',
      "  echo found",
      "fi",
      "git check-ignore -q .stride.json || exit 1",
      "uv run python -c 'print(1)'",
      "for path in a b; do",
      "done",
      "while read line; do :",
      "until false; do :",
      'case "$mode" in',
      "esac",
      "node -e 'console.log(1)'",
      "```",
    ].join("\n");

    deepStrictEqual(logicLines(block), [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]);
  });

  it("lets a keyword through in a comment, a string or prose", () => {
    const markdown = [
      "```bash",
      "# repeat for each PR, then done",
      'echo "if this fails; then retry"',
      "```",
      "```",
      "/linear:fix PG-X  → address review feedback (if any)",
      "```",
      "```graphql",
      "query { issues { nodes { id } } }",
      "```",
    ].join("\n");

    deepStrictEqual(logicLines(markdown), []);
  });
});
