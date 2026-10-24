// Parses Mermaid diagrams with the Mermaid version properdocs.yml pins in
// `extra.mermaid_version`, so a diagram that would render as "Syntax error in text" on the
// site fails here instead. Run `npm ci` in this directory first. Exits
// non-zero on any problem.
//
//   node check-mermaid.mjs              every ```mermaid fence in tracked Markdown
//   node check-mermaid.mjs --site site  every diagram in a built site, as the
//                                       browser receives it
//
// Both are needed: a valid fence can still be mangled by the build, as HTML
// minification once collapsed every diagram onto one line.
import { execFileSync } from "node:child_process";
import { readdirSync, readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { JSDOM } from "jsdom";

// Mermaid sanitizes labels with DOMPurify, which needs a window to exist
// before it is first imported.
const { window } = new JSDOM("");
globalThis.window = window;
globalThis.document = window.document;
const { default: mermaid } = await import("mermaid");

const root = execFileSync("git", ["rev-parse", "--show-toplevel"], { encoding: "utf8" }).trim();

// Parsing with one version and rendering with another would prove nothing.
const pinned = readFileSync(`${root}/properdocs.yml`, "utf8").match(/^\s+mermaid_version:\s*(\S+)/m)?.[1];
const installed = createRequire(import.meta.url)("mermaid/package.json").version;
if (pinned !== installed) {
  console.error(`properdocs.yml pins mermaid ${pinned}, but ${installed} is installed. Update package.json to match.`);
  process.exit(1);
}

function* fromMarkdown() {
  const files = execFileSync("git", ["ls-files", "-z", "*.md"], { cwd: root, encoding: "utf8" }).split("\0").filter(Boolean);
  for (const file of files) {
    const lines = readFileSync(`${root}/${file}`, "utf8").split("\n");
    for (let i = 0; i < lines.length; i++) {
      const open = lines[i].match(/^(\s*)(`{3,}|~{3,})\s*mermaid\s*$/);
      if (!open) continue;
      const [, indent, fence] = open;
      const start = i + 1;
      const body = [];
      for (i++; i < lines.length; i++) {
        const close = lines[i].match(/^\s*(`{3,}|~{3,})\s*$/);
        if (close && close[1][0] === fence[0] && close[1].length >= fence.length) break;
        body.push(lines[i].startsWith(indent) ? lines[i].slice(indent.length) : lines[i]);
      }
      yield [`${file}:${start}`, body.join("\n")];
    }
  }
}

// The build emits each diagram as <div class="mermaid">, and Mermaid 10.4
// reads that div's innerHTML and decodes its entities, keeping tags such as
// <br> as text. The div goes through an HTML parse first, as it does in the
// browser, because an unescaped tag would be rewritten there: `<Project>` in a
// label comes back as `<project>...</project>`.
function* fromSite(dir) {
  const holder = window.document.createElement("div");
  const decoder = window.document.createElement("textarea");
  const pages = readdirSync(dir, { recursive: true }).filter((f) => f.endsWith(".html")).sort();
  for (const page of pages) {
    const html = readFileSync(`${dir}/${page}`, "utf8");
    for (const match of html.matchAll(/<div\b[^>]*\bclass=["']?mermaid\b["']?[^>]*>[\s\S]*?<\/div>/g)) {
      holder.innerHTML = match[0];
      decoder.innerHTML = holder.firstElementChild.innerHTML;
      const line = html.slice(0, match.index).split("\n").length;
      yield [`${dir}/${page}:${line}`, decoder.value.trim()];
    }
  }
}

const siteFlag = process.argv.indexOf("--site");
const diagrams = siteFlag === -1 ? fromMarkdown() : fromSite(process.argv[siteFlag + 1]);

let count = 0;
let problems = 0;
for (const [where, text] of diagrams) {
  count++;
  try {
    await mermaid.parse(text);
  } catch (error) {
    problems++;
    console.error(`${where}: ${String(error.message ?? error).trim()}\n`);
  }
}

console.log(`${count} diagrams, ${problems} problems`);
// None at all means the search is wrong, not that every diagram is fine.
process.exit(problems || !count ? 1 : 0);
