import { existsSync, rmSync } from "node:fs";
import { join } from "node:path";
import { contentsMatch, copyFile, walkFiles } from "../../files.mjs";
import { HOOKS_FILE, writeCodexHooks } from "./hooks.mjs";
import { COMMANDS_ROOT, renderCodexSkills, SKILLS_ROOT } from "./skills.mjs";

export const codex = {
  root: ".codex",
  generates: [`${SKILLS_ROOT}/`, HOOKS_FILE],

  install({ srcRoot, destRoot, skills }) {
    for (const skill of skills) copySkill(srcRoot, destRoot, skill);
    const rendered = renderCodexSkills(destRoot);
    writeCodexHooks(destRoot);
    return [
      `Set up Codex CLI in ${SKILLS_ROOT}/: ${skills.length} skill(s), ${rendered.length} command skill(s).`,
      `Wrote ${HOOKS_FILE} — trust the hooks with /hooks in Codex or they will not run.`,
    ];
  },

  uninstall({ srcRoot, destRoot, skills }) {
    rmSync(join(destRoot, HOOKS_FILE), { force: true });
    for (const name of generatedNames(srcRoot, skills)) {
      rmSync(join(destRoot, SKILLS_ROOT, name), {
        recursive: true,
        force: true,
      });
    }
  },
};

function copySkill(srcRoot, destRoot, name) {
  const srcDir = join(srcRoot, ".claude/skills", name);
  for (const rel of walkFiles(srcDir)) {
    const srcFile = join(srcDir, rel);
    const destFile = join(destRoot, SKILLS_ROOT, name, rel);
    if (existsSync(destFile) && contentsMatch(srcFile, destFile)) continue;
    copyFile(srcFile, destFile);
  }
}

function generatedNames(srcRoot, skills) {
  const commandsDir = join(srcRoot, COMMANDS_ROOT, "linear");
  if (!existsSync(commandsDir)) return skills;
  const commands = walkFiles(commandsDir)
    .filter((rel) => rel.endsWith(".md") && !rel.includes("/"))
    .map((rel) => `linear-${rel.replace(/\.md$/, "")}`);
  return [...skills, ...commands];
}
