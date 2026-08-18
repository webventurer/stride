// Renders one Codex skill per stride command. Codex has no namespaced slash
// commands, so `/linear:start` can't survive the mapping — each command becomes
// a skill invoked as `$linear-start`, pointing at the command file rather than
// copying it, so `.claude/commands/` stays the only place a body is authored.

import { mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

export const COMMANDS_ROOT = ".claude/commands";
export const SKILLS_ROOT = ".codex/skills";

const NAMESPACE = "linear";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILL_TEMPLATE = join(__dirname, "templates/codex-skill.md");

export function renderCodexSkills(repoRoot) {
  const commandsDir = join(repoRoot, COMMANDS_ROOT, NAMESPACE);
  const skills = commandFiles(commandsDir).map((file) =>
    planSkill(commandsDir, file),
  );

  for (const skill of skills) writeSkill(repoRoot, skill);
  return skills.map((skill) => skill.name);
}

function commandFiles(commandsDir) {
  return readdirSync(commandsDir, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
    .map((entry) => entry.name)
    .sort();
}

function planSkill(commandsDir, file) {
  const description = frontmatterDescription(
    readFileSync(join(commandsDir, file), "utf8"),
  );
  if (!description) {
    throw new Error(
      `${join(COMMANDS_ROOT, NAMESPACE, file)} has no frontmatter description — ` +
        "Codex skips commands without one, so add a description before rendering.",
    );
  }
  const stem = file.replace(/\.md$/, "");
  return {
    name: `${NAMESPACE}-${stem}`,
    description,
    commandRef: `${COMMANDS_ROOT}/${NAMESPACE}/${file}`,
  };
}

function frontmatterDescription(content) {
  const frontmatter = content.match(/^---\n([\s\S]*?)\n---\n/);
  if (!frontmatter) return null;
  const description = frontmatter[1].match(/^description:[ \t]*(.+)$/m);
  return description ? description[1].trim() : null;
}

function writeSkill(repoRoot, skill) {
  const dir = join(repoRoot, SKILLS_ROOT, skill.name);
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, "SKILL.md"), renderSkill(skill));
}

function renderSkill({ name, description, commandRef }) {
  return fillTemplate(readFileSync(SKILL_TEMPLATE, "utf8"), {
    NAME: name,
    DESCRIPTION: description,
    COMMAND_REF: commandRef,
  });
}

function fillTemplate(template, values) {
  return template.replace(
    /\{\{(\w+)\}\}/g,
    (placeholder, key) => values[key] ?? placeholder,
  );
}
