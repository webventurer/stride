import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const COMMANDS_DIR = ".claude/commands/linear";

const ORDER = [
  "check",
  "setup",
  "start",
  "plan-work",
  "quick",
  "fix",
  "finish",
  "next-steps",
  "list-projects",
  "update-vision",
];

export function linearCommandNames(srcRoot) {
  const dir = join(srcRoot, COMMANDS_DIR);
  if (!existsSync(dir)) return [];
  const names = readdirSync(dir)
    .filter((entry) => entry.endsWith(".md"))
    .map((entry) => entry.replace(/\.md$/, ""));
  return [...names].sort(byWorkflowOrder);
}

function byWorkflowOrder(a, b) {
  return rank(a) - rank(b) || a.localeCompare(b);
}

function rank(name) {
  const index = ORDER.indexOf(name);
  return index === -1 ? ORDER.length : index;
}

export function linearCommandLines(srcRoot) {
  return linearCommandNames(srcRoot).map((name) =>
    `  ${`/linear:${name}`.padEnd(22)}— ${summary(srcRoot, name)}`.trimEnd(),
  );
}

function summary(srcRoot, name) {
  const text = readFileSync(join(srcRoot, COMMANDS_DIR, `${name}.md`), "utf8");
  const description = text.match(/^---\n[\s\S]*?description:\s*(.+)/)?.[1];
  return description ? firstSentence(description.trim()) : "";
}

function firstSentence(description) {
  const sentence = description.match(/^.*?\.(?:\s|$)/)?.[0].trim();
  return (sentence ?? description).replace(/\.$/, "");
}
