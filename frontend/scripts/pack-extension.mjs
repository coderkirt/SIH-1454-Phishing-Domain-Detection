/**
 * Copy the Chrome MV3 extension into public/phisheye-extension.zip
 * and bake the live FastAPI + dashboard URLs into config.js.
 *
 * Local: keeps 127.0.0.1 defaults unless VITE_API_URL is set.
 * Render: VITE_API_URL and RENDER_EXTERNAL_URL / VITE_DASHBOARD_URL.
 */
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { cp } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { crc32, deflateRawSync } from "node:zlib";

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
writeZip(stagingDir, zipPath);
rmSync(stagingDir, { recursive: true, force: true });
console.log(`Packed ${zipPath}`);
console.log(`  API       ${apiUrl}`);
console.log(`  Dashboard ${dashboardUrl}`);

function walkFiles(dir, prefix = "") {
  const out = [];
  for (const name of readdirSync(dir)) {
    const full = path.join(dir, name);
    const rel = prefix ? `${prefix}/${name}` : name;
    if (statSync(full).isDirectory()) out.push(...walkFiles(full, rel));
    else out.push({ full, rel: rel.replaceAll("\\", "/") });
  }
  return out;
}

/** Real PK zip. `tar -a` on Linux writes a tar named .zip, which Windows cannot open. */
function writeZip(fromDir, outFile) {
  const files = walkFiles(fromDir);
  const locals = [];
  const centrals = [];
  let offset = 0;
  for (const file of files) {
    const data = readFileSync(file.full);
    const compressed = deflateRawSync(data);
    const checksum = crc32(data) >>> 0;
    const name = Buffer.from(file.rel, "utf8");
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(20, 4);
    local.writeUInt16LE(8, 8);
    local.writeUInt32LE(checksum, 14);
    local.writeUInt32LE(compressed.length, 18);
    local.writeUInt32LE(data.length, 22);
    local.writeUInt16LE(name.length, 26);
    const localFull = Buffer.concat([local, name, compressed]);
    locals.push(localFull);

    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0);
    central.writeUInt16LE(20, 4);
    central.writeUInt16LE(20, 6);
    central.writeUInt16LE(8, 10);
    central.writeUInt32LE(checksum, 16);
    central.writeUInt32LE(compressed.length, 20);
    central.writeUInt32LE(data.length, 24);
    central.writeUInt16LE(name.length, 28);
    central.writeUInt32LE(offset, 42);
    centrals.push(Buffer.concat([central, name]));
    offset += localFull.length;
  }
  const centralDir = Buffer.concat(centrals);
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);
  eocd.writeUInt16LE(files.length, 8);
  eocd.writeUInt16LE(files.length, 10);
  eocd.writeUInt32LE(centralDir.length, 12);
  eocd.writeUInt32LE(offset, 16);
  writeFileSync(outFile, Buffer.concat([...locals, centralDir, eocd]));
}
