// Checks the CLIs stride's workflow needs before anything is written, and
// stops the install if any are absent — half an install leaves a broken state.
// Install commands mirror docs/install.md so the two never drift. Native
// Windows cannot run the POSIX probes at all, so it is pointed at WSL rather
// than told every tool is missing.

import { execSync } from "node:child_process";

export const PREREQS = [
  { cmd: "gh", install: "brew install gh" },
  { cmd: "uv", install: "brew install uv" },
  { cmd: "jq", install: "brew install jq" },
];

export function missingPrereqs(isPresent = onPath) {
  return PREREQS.filter((p) => !isPresent(p.cmd));
}

export function prereqReport(missing) {
  if (missing.length === 0) return ["Prerequisites: gh, uv, jq all found."];
  return [
    "Missing prerequisites — stride needs these on your PATH. Install them, then re-run:",
    ...missing.map((p) => `  ${p.cmd} — ${p.install}`),
    "  (Non-macOS or no Homebrew? See docs/install.md. install.mjs won't run these for you.)",
  ];
}

export function windowsReport() {
  return [
    "stride requires WSL on Windows — its commit hooks need a bash/zsh",
    "shell. Install WSL, then run the install from inside it. See the",
    "Windows section of docs/install.md.",
  ];
}

export function requirePrerequisites(
  isPresent = onPath,
  log = console.log,
  exit = process.exit,
  platform = process.platform,
) {
  log("");
  if (platform === "win32") {
    for (const line of windowsReport()) log(line);
    exit(1);
    return;
  }
  const missing = missingPrereqs(isPresent);
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
