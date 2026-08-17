// Renders one Codex skill per stride command.
//
// Codex has no namespaced slash commands, so `/linear:start` cannot survive the
// mapping — each command becomes a skill invoked as `$linear-start`. The skill
// points at the command file instead of copying it, so `.claude/commands/` stays
// the only place a command body is authored.

import { mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

export const COMMANDS_ROOT = ".claude/commands";
export const SKILLS_ROOT = ".codex/skills";

// The only command namespace stride ships.
const NAMESPACE = "linear";

function parseDescription(content) {
  const frontmatter = content.match(/^---\n([\s\S]*?)\n---\n/);
  if (!frontmatter) return null;
  const description = frontmatter[1].match(/^description:[ \t]*(.+)$/m);
  return description ? description[1].trim() : null;
}

function renderSkill({ name, description, commandRef }) {
  return `---
name: ${name}
description: ${description}
---

# ${name}

Read \`${commandRef}\` in full, then carry out every step it describes.

Treat whatever the user typed alongside the skill mention as the command's
argument.
`;
}

function commandFiles(commandsDir) {
  return readdirSync(commandsDir, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
    .map((entry) => entry.name)
    .sort();
}

function planSkill(commandsDir, file) {
  const description = parseDescription(
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

export function renderCodexSkills(repoRoot) {
  const commandsDir = join(repoRoot, COMMANDS_ROOT, NAMESPACE);
  const skills = commandFiles(commandsDir).map((file) =>
    planSkill(commandsDir, file),
  );

  for (const skill of skills) {
    const dir = join(repoRoot, SKILLS_ROOT, skill.name);
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, "SKILL.md"), renderSkill(skill));
  }
  return skills.map((skill) => skill.name);
}
