export const SHIPPED_SKILLS = [
  {
    name: "vision",
    blurb: "project Vision authoring skill",
    usage: "author the project Vision (run this first)",
  },
  {
    name: "commit",
    blurb: "multi-pass atomic commit skill",
    usage: "multi-pass atomic git commits",
  },
  {
    name: "craft",
    blurb: "CRAFT prompt skill",
    usage: "CRAFT prompt framework",
  },
  {
    name: "clear-speak",
    blurb: "plain-language rewrite skill",
    usage: "rewrite jargon into plain language",
  },
];

export const SKILL_NAMES = SHIPPED_SKILLS.map((skill) => skill.name);

export function skillFootprintLines() {
  return SHIPPED_SKILLS.map(
    ({ name, blurb }) => `  ${`skills/${name}/`.padEnd(20)}(${blurb})`,
  );
}

export function skillCommandLines() {
  return SHIPPED_SKILLS.map(
    ({ name, usage }) => `  ${`/${name}`.padEnd(22)}— ${usage}`,
  );
}
