/**
 * Copy the Chrome MV3 extension into public/phisheye-extension.zip
 * and bake the live FastAPI + dashboard URLs into config.js.
 *
 * Local: keeps 127.0.0.1 defaults unless VITE_API_URL is set.
 * Render: VITE_API_URL and RENDER_EXTERNAL_URL / VITE_DASHBOARD_URL.
 */
import { createWriteStream, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { cp } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const frontendDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = path.resolve(frontendDir, "..");
const sourceDir = path.join(repoRoot, "extension");
const publicDir = path.join(frontendDir, "public");
const stagingDir = path.join(frontendDir, ".extension-pack");
const zipPath = path.join(publicDir, "phisheye-extension.zip");

function trimSlash(url) {
  return String(url || "").trim().replace(/\/+$/, "");
}

const apiUrl = trimSlash(process.env.VITE_API_URL || "http://127.0.0.1:8000");
const dashboardUrl = trimSlash(
  process.env.VITE_DASHBOARD_URL || process.env.RENDER_EXTERNAL_URL || "http://127.0.0.1:5173",
);

if (!existsSync(sourceDir)) {
  console.error("extension/ folder not found at", sourceDir);
  process.exit(1);
}

rmSync(stagingDir, { recursive: true, force: true });
mkdirSync(publicDir, { recursive: true });
await cp(sourceDir, stagingDir, {
  recursive: true,
  filter: (src) => {
    const name = path.basename(src);
    if (name === "__pycache__" || name === ".DS_Store" || name.endsWith(".pyc")) return false;
    if (name === "make_icons.py") return false;
    return true;
  },
});

const configPath = path.join(stagingDir, "utils", "config.js");
let config = readFileSync(configPath, "utf8");
config = config.replace(
  /export const DEFAULT_API_BASE_URL = "[^"]+";/,
  `export const DEFAULT_API_BASE_URL = ${JSON.stringify(apiUrl)};`,
);
config = config.replace(
  /export const DEFAULT_DASHBOARD_URL = "[^"]+";/,
  `export const DEFAULT_DASHBOARD_URL = ${JSON.stringify(dashboardUrl)};`,
);
writeFileSync(configPath, config);

writeFileSync(
  path.join(stagingDir, "INSTALL.txt"),
  [
    "PHISHEYE Chrome extension (scan-before-open)",
    "",
    `API:       ${apiUrl}`,
    `Dashboard: ${dashboardUrl}`,
    "",
    "1. Unzip this folder.",
    "2. Chrome → chrome://extensions → Developer mode ON.",
    "3. Load unpacked → select the unzipped folder (the one with manifest.json).",
    "4. Pin PHISHEYE. Open github.com (should gate then auto-open if LOW).",
    "5. Do not open live phishing kits in the jury browser.",
    "",
  ].join("\n"),
);

rmSync(zipPath, { force: true });

function zipWithTar() {
  execFileSync("tar", ["-a", "-c", "-f", zipPath, "-C", stagingDir, "."], { stdio: "inherit" });
}

try {
  zipWithTar();
} catch {
  await zipFallback(stagingDir, zipPath);
}

rmSync(stagingDir, { recursive: true, force: true });
console.log(`Packed ${zipPath}`);
console.log(`  API       ${apiUrl}`);
console.log(`  Dashboard ${dashboardUrl}`);

async function zipFallback(fromDir, outFile) {
  const { createRequire } = await import("node:module");
  let archiver;
  try {
    archiver = createRequire(import.meta.url)("archiver");
  } catch {
    throw new Error("Could not create zip (tar failed and archiver is not installed).");
  }
  await new Promise((resolve, reject) => {
    const output = createWriteStream(outFile);
    const archive = archiver("zip", { zlib: { level: 9 } });
    output.on("close", resolve);
    archive.on("error", reject);
    archive.pipe(output);
    archive.directory(fromDir, false);
    archive.finalize();
  });
}
