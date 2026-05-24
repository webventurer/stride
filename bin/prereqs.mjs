import { execSync } from "node:child_process";

// The CLIs the /linear:* workflow needs on PATH. Install commands mirror
// docs/install.md so the two never drift; brew covers macOS and Linux.
export const PREREQS = [
  { cmd: "gh", install: "brew install gh" },
  { cmd: "uv", install: "brew install uv" },
  {
    cmd: "linctl",
    install: "brew tap dorkitude/linctl && brew install linctl",
  },
  { cmd: "jq", install: "brew install jq" },
];

// The prereqs absent from PATH. `isPresent` is injectable so tests don't shell out.
export function missingPrereqs(isPresent = onPath) {
  return PREREQS.filter((p) => !isPresent(p.cmd));
}

// The lines the doctor prints — pure, so tests assert on the array.
export function prereqReport(missing) {
  if (missing.length === 0)
    return ["Prerequisites: gh, uv, linctl, jq all found."];
  return [
    "Missing prerequisites — stride needs these on your PATH. Install them, then re-run:",
    ...missing.map((p) => `  ${p.cmd} — ${p.install}`),
    "  (Non-macOS or no Homebrew? See docs/install.md. install.mjs won't run these for you.)",
  ];
}

// Blocking gate: print the report, and stop the installer if anything is
// missing — stride's /linear:* workflow can't run without these tools, so
// installing half of stride leaves a broken state.
export function requirePrerequisites(
  isPresent = onPath,
  log = console.log,
  exit = process.exit,
) {
  const missing = missingPrereqs(isPresent);
  log("");
  for (const line of prereqReport(missing)) log(line);
  if (missing.length > 0) exit(1);
}

function onPath(cmd) {
  try {
    execSync(`command -v ${cmd}`, { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}
