// Verify the package through an actual clean consumer install, not its source tree.
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync, existsSync } from "node:fs";
import { createRequire } from "node:module";
import { resolve, dirname } from "node:path";

const consumer = resolve(process.argv[2] || "build/npm-smoke");
const require = createRequire(resolve(consumer, "package.json"));
const metadata = require("@sunnyai/sunny-marker/package.json");
const root = dirname(require.resolve("@sunnyai/sunny-marker/package.json"));
const css = readFileSync(require.resolve("@sunnyai/sunny-marker/css"), "utf8");
const next = readFileSync(require.resolve("@sunnyai/sunny-marker/next"), "utf8");
const manifest = JSON.parse(readFileSync(new URL("../fonts/manifest.json", import.meta.url)));
const font = readFileSync(require.resolve("@sunnyai/sunny-marker/files/SunnyMarker-Variable.woff2"));
const expected = manifest.files.find(({ path }) => path === "fonts/webfonts/SunnyMarker-Variable.woff2");

assert.equal(metadata.version, `${manifest.version}.0`);
assert.deepEqual(metadata.dependencies || {}, {});
assert.deepEqual(metadata.scripts || {}, {});
assert.equal(existsSync(resolve(consumer, "node_modules/next")), false, "CSS install pulled in Next.js");
assert.equal(createHash("sha256").update(font).digest("hex"), expected.sha256);
assert.match(css, /font-weight: 300 700/);
assert.match(css, /font-stretch: 75% 125%/);
assert.match(css, /font-style: oblique 0deg 9deg/);
assert.match(next, /export const SunnyMarker = localFont/);
assert.equal(readFileSync(resolve(root, "OFL.txt"), "utf8"), readFileSync(new URL("../OFL.txt", import.meta.url), "utf8"));
console.log(`Verified ${metadata.name}@${metadata.version}: exact release font, usable exports, OFL and no runtime dependencies or install scripts.`);
