#!/usr/bin/env node

import { createHash } from "node:crypto";
import {
  chmodSync,
  copyFileSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  realpathSync,
  statSync,
  unlinkSync,
  writeFileSync,
} from "node:fs";
import { dirname, join, relative } from "node:path";
import { createInterface } from "node:readline";
import { fileURLToPath } from "node:url";
import { buildSection, removeSection } from "./gitignore.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const srcRoot = join(__dirname, "..");
const destRoot = process.cwd();

const HOOK_CONFIG = {
  hooks: {
    UserPromptSubmit: [
      {
        hooks: [
          {
            type: "command",
            command:
              "$CLAUDE_PROJECT_DIR/.claude/hooks/userpromptsubmit/inject_design_principles.sh",
          },
        ],
      },
    ],
    PreToolUse: [
      {
        matcher: "Bash",
        hooks: [
          {
            type: "command",
            command:
              "$CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse/block_bare_git_commit.sh",
          },
        ],
      },
    ],
  },
};

function ask(question) {
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim().toLowerCase());
    });
  });
}

function deepMerge(base, overlay) {
  for (const [key, val] of Object.entries(overlay)) {
    base[key] = mergeValue(base[key], val);
  }
  return base;
}

function mergeValue(existing, val) {
  if (isObject(existing) && isObject(val)) return deepMerge(existing, val);
  if (Array.isArray(existing) && Array.isArray(val))
    return dedupeHooks(existing, val);
  return val;
}

function isObject(v) {
  return v !== null && typeof v === "object" && !Array.isArray(v);
}

function dedupeHooks(existing, incoming) {
  for (const item of incoming) {
    const isDupe = existing.some(
      (e) => JSON.stringify(e) === JSON.stringify(item),
    );
    if (!isDupe) existing.push(item);
  }
  return existing;
}

const DIRS = [
  ".claude/skills/commit",
  ".claude/skills/craft",
  ".claude/skills/vision",
  ".claude/commands/linear",
  ".claude/hooks",
  ".claude/stride/docs/patterns/git",
  ".claude/stride/docs/concepts",
  ".claude/stride/docs/principles",
  ".claude/tools",
];

const HOOKS = [
  ".claude/hooks/do_commit.sh",
  ".claude/hooks/pretooluse/block_bare_git_commit.sh",
  ".claude/hooks/userpromptsubmit/inject_design_principles.sh",
];

function assertUnderClaudeDir(dir) {
  if (dir.startsWith(".claude/") || dir === ".claude") return;
  console.error(
    `\nERROR: refusing to write outside .claude/: ${dir}\n` +
      `Stride's install footprint is .claude/ only. This is a bug in DIRS.`,
  );
  process.exit(1);
}

function hashFile(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function contentsMatch(srcFile, destFile) {
  return hashFile(srcFile) === hashFile(destFile);
}

function walkFiles(root, base = root) {
  const paths = [];
  for (const entry of readdirSync(root)) {
    const full = join(root, entry);
    const stat = lstatSync(full);
    if (stat.isSymbolicLink()) continue;
    if (stat.isDirectory()) paths.push(...walkFiles(full, base));
    else paths.push(relative(base, full));
  }
  return paths;
}

function planAction(srcFile, destFile) {
  if (!existsSync(destFile)) return "copy";
  if (statSync(destFile).isDirectory()) return "conflict";
  return contentsMatch(srcFile, destFile) ? "skip" : "conflict";
}

function copyFile(srcFile, destFile) {
  mkdirSync(dirname(destFile), { recursive: true });
  copyFileSync(srcFile, destFile);
}

const ACTIONS = {
  copy: (src, dst, rel, s) => {
    copyFile(src, dst);
    s.copied.push(rel);
  },
  skip: (_src, _dst, rel, s) => s.skipped.push(rel),
  conflict: (_src, _dst, rel, s) => s.conflicts.push(rel),
};

function installFile(srcFile, destFile, rel, summary) {
  ACTIONS[planAction(srcFile, destFile)](srcFile, destFile, rel, summary);
}

function emptySummary() {
  return { copied: [], skipped: [], conflicts: [] };
}

function isSymlinkedRoot(rootPath) {
  return existsSync(rootPath) && lstatSync(rootPath).isSymbolicLink();
}

function symlinkedRootMatches(srcDir, rootPath) {
  return walkFiles(srcDir).every((rel) => {
    const dest = join(rootPath, rel);
    return existsSync(dest) && contentsMatch(join(srcDir, rel), dest);
  });
}

async function confirmOverwrite(dir, resolved) {
  const prompt = `\nOverwrite ${dir} (symlinked → ${resolved}) with stride's copy? [Y/n] `;
  const answer = await ask(prompt);
  return !answer || answer === "y" || answer === "yes";
}

function recordAll(srcDir, dir, summary, bucket) {
  for (const rel of walkFiles(srcDir)) summary[bucket].push(join(dir, rel));
}

function copyAndRecord(srcDir, dir, summary) {
  for (const rel of walkFiles(srcDir)) {
    copyFile(join(srcDir, rel), join(destRoot, dir, rel));
    summary.copied.push(join(dir, rel));
  }
}

async function resolveSymlinkedRoot(dir, srcDir, rootPath, summary) {
  const matches = symlinkedRootMatches(srcDir, rootPath);
  if (!(await confirmOverwrite(dir, realpathSync(rootPath))))
    return recordAll(srcDir, dir, summary, matches ? "skipped" : "conflicts");
  unlinkSync(rootPath);
  copyAndRecord(srcDir, dir, summary);
}

async function installDir(dir) {
  const srcDir = join(srcRoot, dir);
  if (!existsSync(srcDir)) return emptySummary();
  assertUnderClaudeDir(dir);
  const summary = emptySummary();
  const rootPath = join(destRoot, dir);
  if (isSymlinkedRoot(rootPath)) {
    await resolveSymlinkedRoot(dir, srcDir, rootPath, summary);
    return summary;
  }
  for (const rel of walkFiles(srcDir)) {
    installFile(
      join(srcDir, rel),
      join(destRoot, dir, rel),
      join(dir, rel),
      summary,
    );
  }
  return summary;
}

function mergeSummary(totals, part) {
  totals.copied.push(...part.copied);
  totals.skipped.push(...part.skipped);
  totals.conflicts.push(...part.conflicts);
}

function reportConflictsAndExit(paths) {
  console.error("\nERROR: target files differ from stride's source:");
  for (const p of paths) console.error(`  ${p}`);
  console.error("\nResolve manually (diff or replace) and re-run.");
  process.exit(1);
}

function makeExecutable(hook) {
  const path = join(destRoot, hook);
  if (existsSync(path)) chmodSync(path, 0o755);
}

async function copyFiles() {
  const totals = emptySummary();
  for (const dir of DIRS) mergeSummary(totals, await installDir(dir));
  HOOKS.forEach(makeExecutable);
  if (totals.conflicts.length > 0) reportConflictsAndExit(totals.conflicts);
  return totals;
}

const LINEAR_OAUTH = {
  linear: {
    command: "npx",
    args: ["-y", "mcp-remote", "https://mcp.linear.app/mcp"],
  },
};

const LINEAR_API_KEY = {
  "linear-org1": {
    command: "npx",
    args: [
      "-y",
      "mcp-remote",
      "https://mcp.linear.app/mcp",
      "--header",
      "Authorization:Bearer ${LINEAR_ORG1_API_KEY}",
    ],
    env: { LINEAR_ORG1_API_KEY: "${LINEAR_ORG1_API_KEY}" },
  },
  "linear-org2": {
    command: "npx",
    args: [
      "-y",
      "mcp-remote",
      "https://mcp.linear.app/mcp",
      "--header",
      "Authorization:Bearer ${LINEAR_ORG2_API_KEY}",
    ],
    env: { LINEAR_ORG2_API_KEY: "${LINEAR_ORG2_API_KEY}" },
  },
};

function isApiKey(method) {
  return method === "api" || method === "apikey";
}

function readMcpConfig(path) {
  if (!existsSync(path)) return { mcpServers: {} };
  const config = JSON.parse(readFileSync(path, "utf8"));
  config.mcpServers = config.mcpServers || {};
  return config;
}

function writeMcpConfig(path, config) {
  writeFileSync(path, `${JSON.stringify(config, null, 2)}\n`);
}

function hasLinearMcp(mcpPath) {
  if (!existsSync(mcpPath)) return false;
  const config = JSON.parse(readFileSync(mcpPath, "utf8"));
  const servers = Object.keys(config.mcpServers || {});
  return servers.some((s) => s.toLowerCase().includes("linear"));
}

async function configureMcp() {
  const mcpPath = join(destRoot, ".mcp.json");
  if (hasLinearMcp(mcpPath)) {
    console.log("Linear MCP already configured in .mcp.json — skipping");
    return;
  }
  const method = await ask(
    "Linear MCP: oauth (single org), api (multiple orgs), or none? [none] ",
  );
  if (!method || method === "none" || method === "n" || method === "skip") {
    console.log("Skipped Linear MCP setup");
    return;
  }
  const servers = isApiKey(method) ? LINEAR_API_KEY : LINEAR_OAUTH;
  const config = readMcpConfig(mcpPath);
  deepMerge(config.mcpServers, servers);
  writeMcpConfig(mcpPath, config);
  console.log(
    isApiKey(method)
      ? "Configured Linear MCP (API key — add LINEAR_ORG1_API_KEY and LINEAR_ORG2_API_KEY to ~/.env)"
      : "Configured Linear MCP (OAuth — browser login on first use)",
  );
}

function mergeSettings() {
  const settingsPath = join(destRoot, ".claude/settings.local.json");
  mkdirSync(dirname(settingsPath), { recursive: true });

  let settings = {};
  if (existsSync(settingsPath)) {
    settings = JSON.parse(readFileSync(settingsPath, "utf8"));
  }

  deepMerge(settings, HOOK_CONFIG);
  writeFileSync(settingsPath, `${JSON.stringify(settings, null, 2)}\n`);
}

async function installFiles() {
  logCopiedFiles(await copyFiles());
}

function installHeader({ copied, skipped }) {
  if (skipped.length === 0) return "Installed to .claude/:";
  return `Installed to .claude/ (${copied.length} new, ${skipped.length} already matched):`;
}

function logCopiedFiles(totals) {
  console.log(installHeader(totals));
  console.log("  skills/vision/   (project Vision authoring skill)");
  console.log("  skills/commit/   (4-pass atomic commit skill)");
  console.log("  skills/craft/    (CRAFT prompt skill)");
  console.log("  commands/linear/ (Linear workflow commands)");
  console.log("  hooks/           (commit hook scripts)");
  console.log("  stride/docs/     (principles, patterns, concepts)");
  console.log("  tools/           (cross-model feedback script)");
}

async function confirmSettingsMerge() {
  const answer = await ask(
    "\nMerge hook config into existing .claude/settings.local.json? [Y/n] ",
  );
  return !answer || answer === "y" || answer === "yes";
}

async function installHookConfig() {
  const existed = existsSync(join(destRoot, ".claude/settings.local.json"));
  if (existed && !(await confirmSettingsMerge())) {
    console.log(
      "Skipped settings merge. You can add the hooks manually — see README.",
    );
    return false;
  }
  mergeSettings();
  console.log(
    existed
      ? "Merged hooks into .claude/settings.local.json"
      : "Created .claude/settings.local.json with hook config",
  );
  return true;
}

function logAvailableSkills() {
  console.log("\nDone. Available skills:");
  console.log(
    "  /vision              — author the project Vision (run this first)",
  );
  console.log("  /commit              — 4-pass atomic git commits");
  console.log("  /craft               — CRAFT prompt framework");
  console.log("  /linear:check        — verify MCP connections");
  console.log("  /linear:start        — implement a Linear issue");
  console.log("  /linear:plan-work    — create a Linear issue");
  console.log("  /linear:fix          — address PR review feedback");
  console.log("  /linear:finish       — merge and close");
  console.log("  /linear:next-steps   — review priorities");
  console.log(
    "\nNext: run /vision to author your project's guiding light. Every /linear:* command reads VISION.md before deciding anything — without one, /linear:plan-work refuses to draft.\n",
  );
}

function gitignoreEntries() {
  const entries = DIRS.filter((d) => d !== ".claude/hooks").map((d) => `${d}/`);
  return [...entries, ...HOOKS].sort();
}

async function confirmGitignoreWrite() {
  const answer = await ask("\nAdd stride paths to .gitignore? [Y/n] ");
  return !answer || answer === "y" || answer === "yes";
}

function writeGitignoreSection() {
  const path = join(destRoot, ".gitignore");
  const existing = existsSync(path) ? readFileSync(path, "utf8") : "";
  const stripped = removeSection(existing);
  const prefix = stripped ? `${stripped.trimEnd()}\n\n` : "";
  writeFileSync(path, `${prefix}${buildSection(gitignoreEntries())}\n`);
}

async function configureGitignore() {
  if (!(await confirmGitignoreWrite())) {
    console.log("Skipped .gitignore update");
    return;
  }
  writeGitignoreSection();
  console.log("Updated .gitignore with stride paths");
}

async function main() {
  console.log("\nstride — All the speed. None of the mess.\n");
  await installFiles();
  await configureGitignore();
  await configureMcp();
  if (!(await installHookConfig())) return;
  logAvailableSkills();
}

main();
