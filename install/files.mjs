import { createHash } from "node:crypto";
import {
  copyFileSync,
  lstatSync,
  mkdirSync,
  readdirSync,
  readFileSync,
} from "node:fs";
import { dirname, join, relative } from "node:path";

const EXCLUDE = new Set(["tests", "__pycache__"]);

export function walkFiles(root, base = root) {
  const paths = [];
  for (const entry of readdirSync(root)) {
    if (EXCLUDE.has(entry)) continue;
    const full = join(root, entry);
    const stat = lstatSync(full);
    if (stat.isSymbolicLink()) continue;
    if (stat.isDirectory()) paths.push(...walkFiles(full, base));
    else paths.push(relative(base, full));
  }
  return paths;
}

export function copyFile(srcFile, destFile) {
  mkdirSync(dirname(destFile), { recursive: true });
  copyFileSync(srcFile, destFile);
}

export function contentsMatch(srcFile, destFile) {
  return hashFile(srcFile) === hashFile(destFile);
}

function hashFile(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}
