#!/usr/bin/env python3
"""Structural checker for a teach workspace.

Usage: check-workspace.py learning/<domain>/<topic> [more workspaces...]

Checks what the `teach` skill's SKILL.md and FORMATS.md specify and a human
reviewer reliably misses: front matter, the H1 against the front-matter title,
the three consecutive bold lines, section presence and order, collapsible-block
shape and nesting, the closing block byte for byte, dashes, forbidden tokens,
machine-specific strings, control characters outside code blocks, trailing
whitespace, the indent a numbered item's continuations carry, relative links,
contiguous lesson numbering, README rows against
lesson front matter, the arc table against the lessons that exist, and glossary
alphabetical order.

Not every rule is universal. Some are one workspace's local convention, and
applying them everywhere produces false positives rather than findings: the
Java workspace marks Practice items with `▢` and ends Going further with its
stage reference sheet, both starting at lesson 7, while the Go and Python
workspaces predate those conventions and do not use them. Those rules live in
CONVENTIONS, keyed by workspace directory name, over the values in DEFAULTS.

Most of them default to off, and a key turns one on for the workspace that
adopted it. A few default to on, because FORMATS.md requires them of every
workspace, and there a key turns one off for an arc written before the rule.
Say which case a new key is, in a comment, and for the second case say what is
tracking the retrofit. Never turn a rule off to quiet a finding.

CONVENTIONS also carries `machine_allow`, for the case where a string on the
machine-specific blacklist is genuinely subject matter in one workspace: the
Python arc has to name the operating systems whose `multiprocessing` start
methods differ, and that is a fact the reader needs.

Exits non-zero if any workspace has a problem.
"""
import re
import sys
import unicodedata
from pathlib import Path

# The house block that closes every lesson, below a --- separator. A final
# lesson may put one paragraph between the separator and the block to close
# the arc, so the two parts are checked separately.
SEPARATOR = "\n---\n"

CLOSING_BODY = (
    "Not landing? Reread the primary source at the top, since this lesson compresses it "
    "and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) "
    "for any term that felt slippery.\n"
    "\n"
    "If the lesson itself is unclear rather than the material, that is a defect: "
    "[open an issue](https://github.com/TokenCemetery/teach/issues).\n"
)

SECTIONS = ["## Warm-up", "## Know this", "## Practice", "## Real-world reps", "## Going further"]

# Lesson 1 has no Warm-up, because there is nothing yet to warm up from.
DEFAULTS = {
    # Lesson number from which every Practice item must carry the ▢ marker.
    # None means the workspace does not use the marker.
    "practice_marker_from": None,
    # Lesson number from which Going further must link the stage reference
    # sheet directly before the Resources bullet. None means no stage sheets.
    "stage_sheet_from": None,
    "min_practice": 3,
    "min_reps": 3,
    # MACHINE patterns this workspace legitimately needs, because the string
    # is subject matter there rather than a leak. Keep each one narrow.
    "machine_allow": (),
    # Whether Going further must end with the Resources bullet. One arc ends
    # each lesson on a forward pointer to the next instead, which is a
    # pedagogical choice rather than drift.
    "resources_bullet_last": True,
    # Whether the arc table must carry a Lessons column tying every lesson to a
    # stage. FORMATS.md requires it, because it is what makes "does every
    # success bullet have a lesson behind it" checkable at all. The six arcs
    # written before the rule are exempt until the column is added to them.
    "arc_lessons_column": True,
}

CONVENTIONS = {
    "java": {"practice_marker_from": 7, "stage_sheet_from": 7,
             "arc_lessons_column": False},
    # Start methods genuinely differ by operating system, so naming one is a
    # fact the reader needs rather than a trace of the author's machine.
    "python": {"machine_allow": (r"\bmacOS\b", r"\bWindows 1\d\b"),
               "arc_lessons_column": False},
    # These arcs predate the Lessons column and carry 290 lessons between them,
    # so assigning each to a stage is judgment work rather than a mechanical
    # edit. Exempt rather than retrofitted; tracked in issue #99.
    "golang": {"arc_lessons_column": False},
    "rust": {"arc_lessons_column": False},
    "sql": {"arc_lessons_column": False},
    # This arc ends 26 of its 27 Going further sections on a forward pointer
    # to the lesson that pays the material off, or on the reference sheets it
    # earned, rather than on the Resources bullet. It is consistent enough to
    # be the convention there, and the arc is closed, so it is exempt rather
    # than retrofitted.
    "finetuning": {"resources_bullet_last": False},
    # This arc has used the box marker since its first lesson, in the Warm-up
    # as well as in Practice, so it is enforced from lesson 1 rather than from
    # the lesson Java happened to adopt it at.
    "typescript": {"practice_marker_from": 1, "arc_lessons_column": False},
}

# Strings that identify the machine a lesson was drafted on rather than a fact
# about the subject. Lessons are written for any reader, so none of these may
# reach a published file. Versions a lesson deliberately pins are project
# facts and belong here only when they match a locally installed build.
# Two groups, because they are forbidden for different reasons and one group
# also applies to the unpublished NOTES.md while the other deliberately does not.
#
# LEAK: says something about this checkout or this person rather than about the
# subject, and is never the finding. A path or a username is noise in a lesson
# and a small privacy leak in a committed note, so it is banned in both.
MACHINE_LEAK = [
    r"/Users/", r"olegshulyakov", r"/tmp/javawork",
    r"/opt/homebrew", r"\$ cd /", r"~/Projects",
    # This machine's time zone. A tool that prints a local timestamp stamps
    # its offset on the output, so a pasted log or query result carries the
    # author's zone unless the run was told to use UTC.
    r"\+0300\b", r"\+03:00\b", r"\bMSK\b", r"\bru_RU\b",
]

# ENV: names the platform, the editor or the exact installed build. Forbidden in
# a published lesson, where it tells a reader about the author's machine instead
# of about the subject. **Allowed in NOTES.md**, which exists to record which
# build produced a finding: "rechecked on Maven 3.9.16" is provenance there and
# noise in a lesson, and a finding is sometimes about the platform itself.
MACHINE_ENV = [
    r"\bDarwin\b", r"\bzsh\b", r"\bHomebrew\b", r"\bbrew install\b",
    r"25\.0\.\d+\.\d+", r"\bmacOS\b", r"\bWindows 1\d\b",
    r"\b3\.9\.16\b", r"\bopenjdk@2\d\b",
    r"\bIntelliJ\b", r"\bVS Code\b",
]

MACHINE = MACHINE_LEAK + MACHINE_ENV

# Draft markers and tool-call syntax that must never survive into a lesson.
# "placeholder" on its own is ordinary technical vocabulary (display-name
# placeholders, resource-filtering placeholders), so match only stub forms.
FORBIDDEN = [
    "<invoke name=", "<parameter name=", "antml:", "TODO", "TBD", "FIXME",
    "XXX", "coming soon", "Lorem ipsum",
    "placeholder text", "[placeholder]", "<placeholder>",
]

FENCE = re.compile(r"^\s*(```|~~~)", re.M)

# The site's markdown extensions, kept in step with mkdocs.yml. Rendering with
# these is the only check that actually proves a collapsible block survives,
# rather than proving it looks right in the source. Available only when the
# project virtual environment's interpreter runs this script; without it the
# render check is reported as skipped rather than passing silently.
SITE_EXTENSIONS = ["md_in_html", "sane_lists", "nl2br",
                   "pymdownx.highlight", "pymdownx.superfences"]
try:
    import markdown as _markdown
except ImportError:
    _markdown = None


def strip_code(text):
    """Remove fenced blocks and inline code spans."""
    out, in_fence = [], False
    for line in text.split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(re.sub(r"`[^`]*`", "", line))
    return "\n".join(out)


def md_unescape(text):
    """Drop the backslash from a markdown escape.

    A heading sometimes has to escape a character to render at all: the
    trailing-`#` rule below requires `\\#`, so a lesson titled `Reviewing C#`
    has an H1 reading `# Lesson 31. Reviewing C\\#`. Both renderers treat a
    backslash before ASCII punctuation as an escape and drop it, so undo the
    same set here before comparing a heading against a front-matter title.
    """
    return re.sub(r"\\([!-/:-@\[-`{-~])", r"\1", text)


def unquote(text):
    """Unwrap a YAML front-matter value that is quote-delimited.

    Only strips a leading/trailing `"` when both are present, so a value
    that merely ends with a quoted word (e.g. a description ending in
    `"majority agreement"`) is left untouched instead of losing one quote.
    """
    if len(text) >= 2 and text.startswith('"') and text.endswith('"'):
        return text[1:-1]
    return text


def code_free_lines(text):
    """Yield (lineno, line) for lines outside fenced blocks."""
    in_fence = False
    for i, line in enumerate(text.split("\n"), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield i, line


class Workspace:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.conv = dict(DEFAULTS, **CONVENTIONS.get(self.root.name, {}))
        self.problems = []
        self.meta = {}
        self.sheets = []

    def bad(self, where, msg):
        self.problems.append(f"{where}: {msg}")

    def uses(self, key, lesson_num):
        """True when a per-workspace convention applies to this lesson."""
        start = self.conv[key]
        return start is not None and lesson_num >= start

    # --- per-file checks -------------------------------------------------

    def check_lesson(self, path, rel, n_expected):
        text = path.read_text(encoding="utf-8")
        lines = text.split("\n")

        if not text.startswith("---\n"):
            self.bad(rel, "does not open with front matter")
            return None
        end = text.find("\n---\n", 4)
        if end < 0:
            self.bad(rel, "front matter is not closed")
            return None
        fm = {}
        for line in text[4:end + 1].strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()

        for key in ("title", "description", "type"):
            if key not in fm:
                self.bad(rel, f"front matter is missing `{key}`")
        if fm.get("type") != "lesson":
            self.bad(rel, f"type is {fm.get('type')!r}, expected 'lesson'")

        title = unquote(fm.get("title", ""))
        m = re.match(r"^(\d+)\. (.+)$", title)
        if not m:
            self.bad(rel, f"title {title!r} is not 'N. Title'")
            num, headline = None, None
        else:
            num, headline = int(m.group(1)), m.group(2)
            if num != n_expected:
                self.bad(rel, f"title numbers this lesson {num}, filename says {n_expected}")

        desc = unquote(fm.get("description", ""))
        if not desc:
            self.bad(rel, "description is empty")
        elif desc.endswith("."):
            self.bad(rel, "description ends with a full stop")

        # Compare with escapes undone. A title ending in `#`, such as
        # `31. Reviewing C#`, has to be written `# Lesson 31. Reviewing C\#`
        # to survive the trailing-`#` rule further down, and the front matter
        # carries no backslash. Comparing the raw line made those two rules
        # impossible to satisfy at once.
        h1 = next((l for l in lines if l.startswith("# ")), None)
        if h1 is None:
            self.bad(rel, "has no H1")
        elif headline is not None and md_unescape(h1) != f"# Lesson {num}. {headline}":
            self.bad(rel, f"H1 {h1!r} does not match front-matter title {title!r}")

        # The three bold lines, on three consecutive lines.
        idx = next((i for i, l in enumerate(lines) if l.startswith("**Mission link:**")), None)
        if idx is None:
            self.bad(rel, "has no **Mission link:** line")
        else:
            for off, label in ((1, "**Primary source:**"), (2, "**Prerequisites:**")):
                if idx + off >= len(lines) or not lines[idx + off].startswith(label):
                    self.bad(rel, f"{label} must be on the line directly after the previous one")

        expected = SECTIONS if n_expected > 1 else SECTIONS[1:]
        seen = [l for l in lines if l in SECTIONS]
        if seen != expected:
            self.bad(rel, f"section headings are {seen}, expected {expected}")
        for s in SECTIONS:
            if lines.count(s) > 1:
                self.bad(rel, f"{s} appears {lines.count(s)} times")

        # Only the Practice section takes the ▢ marker. A numbered list in
        # Know this is ordinary prose, such as a procedure the reader follows.
        try:
            p_start = lines.index("## Practice")
            p_end = lines.index("## Real-world reps")
            practice_lines = lines[p_start:p_end]
        except ValueError:
            practice_lines = lines
        practice = [l for l in practice_lines if re.match(r"^\d+\. ", l)]
        if self.uses("practice_marker_from", n_expected):
            for l in practice:
                if not re.match(r"^\d+\. ▢ ", l):
                    self.bad(rel, f"practice item lacks the ▢ marker: {l[:60]!r}")
        if len(practice) < self.conv["min_practice"]:
            self.bad(rel, f"only {len(practice)} practice items")

        reps = [l for l in lines if l.startswith("- [ ]")]
        if len(reps) < self.conv["min_reps"]:
            self.bad(rel, f"only {len(reps)} real-world reps")
        if not any(l.startswith("- [ ] Tomorrow:") for l in reps):
            self.bad(rel, "no rep begins '- [ ] Tomorrow:'")
        if any(l.startswith(("- [x]", "- [X]")) for l in lines):
            self.bad(rel, "a rep is pre-ticked")

        try:
            gf = lines.index("## Going further")
            tail = [l for l in lines[gf:] if l.startswith("- ")]
            if not tail:
                self.bad(rel, "Going further has no bullets")
            elif not self.conv["resources_bullet_last"]:
                pass
            elif tail[-1] != "- [Resources](../RESOURCES.md)":
                self.bad(rel, f"last Going further bullet is {tail[-1]!r}, "
                              "expected '- [Resources](../RESOURCES.md)'")
            elif self.uses("stage_sheet_from", n_expected):
                if len(tail) < 2:
                    self.bad(rel, "Going further needs the stage sheet before Resources")
                elif not any(f"../reference/{s}" in tail[-2] for s in self.sheets):
                    self.bad(rel, "second-to-last Going further bullet is not a "
                                  f"reference sheet: {tail[-2][:70]!r}")
        except ValueError:
            pass

        _, sep, tail = text.rpartition(SEPARATOR)
        if not sep or not tail.endswith("\n" + CLOSING_BODY):
            self.bad(rel, "closing block does not match the house block byte for byte")
        else:
            extra = tail[:-len("\n" + CLOSING_BODY)].strip()
            if extra and ("\n## " in extra or "<details" in extra or "\n\n" in extra):
                self.bad(rel, "only a single closing paragraph may sit between the "
                              "--- separator and the house block")

        self.check_details(text, lines, rel)
        return {"num": num, "title": headline, "desc": desc}

    def check_details(self, text, lines, rel):
        """Collapsible blocks must render, which the theme is strict about."""
        depth = 0
        for i, line in code_free_lines(text):
            # A backslash before a backtick is never an escape inside a code
            # span, so `\``, which authors reach for when the span's content is
            # itself a backtick, terminates the span at the inner backtick and
            # leaks a stray </code> plus a literal backslash into the page.
            # Template literal types make this likely. Use a fenced block, or
            # pad a doubled delimiter: `` `on${string}` ``.
            # Two of them on one line is the signature: an author wrapping an
            # inner backtick-delimited thing and escaping both ends. One on its
            # own is usually a legitimate span whose content is a backslash,
            # as when a lesson discusses a line-continuation escape.
            if line.count("\\`") >= 2:
                self.bad(rel, f"line {i}: a backslash before a backtick does not escape it "
                              "inside a code span; use a fenced block or a padded `` delimiter")
            # A `<` immediately followed by `?` opens a processing instruction as
            # far as Python-Markdown's HTML block parser is concerned, and that
            # parser runs before inline code is protected, so backticks do not
            # save it. One `List<?>` inside a collapsible block silently stops
            # md_in_html processing that block and every later one in the file,
            # which renders the raw tag and the literal markdown. Write it as
            # <code>List&lt;?&gt;</code>, which renders identically. A space, as
            # in `Map<String, ?>`, is already safe.
            if depth and "<?" in line:
                self.bad(rel, f"line {i}: `<?` inside a collapsible block stops "
                              "md_in_html; write <code>...&lt;?&gt;</code> instead")
            if line.startswith("<details"):
                if line not in ('<details markdown="1"><summary>Check</summary>',
                                '<details markdown="1"><summary>Hint</summary>'):
                    self.bad(rel, f"line {i}: unexpected details opener {line!r}")
                if depth:
                    self.bad(rel, f"line {i}: nested <details>")
                depth += 1
                nxt = lines[i] if i < len(lines) else ""
                if nxt.strip() != "":
                    self.bad(rel, f"line {i}: needs a blank line after <summary>")
                # An answer to "predict the row count" that opens with the
                # number, as in "64. Eight countries times eight customers",
                # is parsed as an ordered list starting at 64 and renders as a
                # list item rather than the sentence it is. A deliberate list
                # in an answer starts at 1, so only a different opening number
                # is the signature of this mistake.
                first = next((lines[j] for j in range(i, min(i + 4, len(lines)))
                              if lines[j].strip()), "")
                m = re.match(r"(\d+)\.\s", first)
                if m and m.group(1) != "1":
                    self.bad(rel, f"line {i}: the answer opens with {m.group(1)!r} and a full "
                                  "stop, which renders as a numbered list item; write the "
                                  "number as a word or put a clause before it")
            elif line.startswith("</details>"):
                if line != "</details>":
                    self.bad(rel, f"line {i}: {line!r} should be exactly '</details>'")
                depth -= 1
                if depth < 0:
                    self.bad(rel, f"line {i}: </details> with no opener")
                prev = lines[i - 2] if i >= 2 else ""
                if prev.strip() != "":
                    self.bad(rel, f"line {i}: needs a blank line before </details>")
            elif "<details" in line or "</details>" in line:
                self.bad(rel, f"line {i}: details tag is not at column zero")
        if depth:
            self.bad(rel, f"{depth} unclosed <details>")

        # A Hint is a sibling directly before its Check, never after it.
        order = re.findall(r"<summary>(Hint|Check)</summary>", strip_code(text))
        for i, kind in enumerate(order):
            if kind == "Hint" and (i + 1 >= len(order) or order[i + 1] != "Check"):
                self.bad(rel, "a Hint block is not directly followed by its Check block")

    def check_prose(self, path, rel):
        text = path.read_text(encoding="utf-8")
        bare = strip_code(text)

        for dash, name in (("—", "em dash"), ("–", "en dash")):
            if dash in bare:
                self.bad(rel, f"contains an {name}")

        for token in FORBIDDEN:
            if token.lower() in bare.lower():
                self.bad(rel, f"contains forbidden token {token!r}")

        for pat in MACHINE:
            if pat in self.conv["machine_allow"]:
                continue
            m = re.search(pat, text)
            if m:
                self.bad(rel, f"contains machine-specific string {m.group(0)!r}")

        # A tab is legitimate inside a fenced block, because real tool output uses one.
        for ch in bare:
            if unicodedata.category(ch) == "Cc" and ch != "\n":
                self.bad(rel, f"control character {ch!r} outside a code block")

        # Python-Markdown strips a run of `#` off the end of an ATX heading
        # without requiring a space in front of it, so `# Learning: C#` shipped
        # as "Learning: C". CommonMark, which GitHub uses, needs that space and
        # keeps the character, so the two renderers of these same files
        # disagree and nothing in the source looks wrong. A backslash fixes it
        # in both: Python-Markdown carries `\#` through the heading parser and
        # unescapes it inline, and CommonMark consumes the backslash too.
        # The backslash this demands is why the H1-against-title check above
        # compares through `md_unescape`; asking for it here and rejecting it
        # there left a title ending in `#` with no spelling that passed both.
        # Excluding a space before the run leaves a real closing sequence,
        # which means the same thing in both renderers, alone. Excluding a `#`
        # as well is what makes that work, since `.*` is greedy enough to eat
        # into the run itself and hand back a `#` as the preceding character.
        for i, line in code_free_lines(text):
            if re.match(r"#{1,6} .*[^\\\s#]#+$", line):
                self.bad(rel, f"line {i}: a trailing '#' on a heading is stripped by "
                              "Python-Markdown but kept by GitHub; escape it as \\#")

        # Python-Markdown keeps a continuation inside its numbered item only at
        # four spaces. At three the ordered list ends, and the continuation
        # renders as a top-level block that happens to sit underneath, which
        # reads almost right. Mixing the two in one item is the damaging case:
        # four-space content following three-space content becomes an indented
        # code block, so an option list added under a three-space fence renders
        # as literal text. Six items were in that state before #51 repaired
        # them.
        #
        # Flagging any three-space line is the wider rule, and it is the one
        # worth having. It catches every mixed item, since a mixed item has a
        # three-space line by definition, and it catches the merely misplaced
        # continuation too, which FORMATS.md also forbids. It is one comparison
        # rather than a per-item indent census, and it fails closed. #53
        # converted the whole corpus to four, so the rule starts from silence.
        #
        # code_free_lines skips fence contents regardless of indentation
        # (#100), so a fenced code sample never trips this check.
        for i, line in code_free_lines(text):
            if re.match(r"^ {3}\S", line):
                self.bad(rel, f"line {i}: continuation indented three spaces, which falls "
                              "out of its numbered item; use four, per FORMATS.md")

        for i, line in enumerate(text.split("\n"), 1):
            if line != line.rstrip():
                self.bad(rel, f"line {i}: trailing whitespace")
        if "\n\n\n\n" in text:
            self.bad(rel, "three or more consecutive blank lines")
        if not text.endswith("\n"):
            self.bad(rel, "no trailing newline")

    def check_notes(self, path, rel):
        """NOTES.md is unpublished: mkdocs.yml excludes it and it carries none of
        the lesson conventions, so the structural rules must not apply. It is
        still committed, though, which is a publication channel of its own, and
        an en dash once survived in one of these files until a manual grep found
        it. So the prose rules and the leak half of the machine rules apply here,
        and MACHINE_ENV deliberately does not: a note recording which build
        produced a finding is provenance, where the same string in a lesson would
        be noise."""
        text = path.read_text(encoding="utf-8")
        bare = strip_code(text)

        for dash, name in (("\u2014", "em dash"), ("\u2013", "en dash")):
            if dash in bare:
                self.bad(rel, f"contains an {name}")

        for pat in MACHINE_LEAK:
            if pat in self.conv["machine_allow"]:
                continue
            m = re.search(pat, text)
            if m:
                self.bad(rel, f"contains machine-specific string {m.group(0)!r}")

        for ch in bare:
            if unicodedata.category(ch) == "Cc" and ch != "\n":
                self.bad(rel, f"control character {ch!r} outside a code block")

        for i, line in enumerate(text.split("\n"), 1):
            if line != line.rstrip():
                self.bad(rel, f"line {i}: trailing whitespace")
        if not text.endswith("\n"):
            self.bad(rel, "no trailing newline")

    def check_render(self, path, rel):
        """Render with the site's extensions and insist every collapsible block
        was actually processed. A block md_in_html skipped is emitted as a raw
        tag with its markdown unparsed, which no source-level rule can see."""
        if _markdown is None:
            return
        src = path.read_text(encoding="utf-8")
        if '<details markdown="1">' not in src:
            return
        body = src.split("---\n", 2)[2] if src.startswith("---\n") else src
        html = _markdown.markdown(body, extensions=SITE_EXTENSIONS)
        left = len(re.findall(r'<details markdown="1">', html))
        if left:
            self.bad(rel, f"{left} collapsible block(s) reached the page unprocessed, "
                          "so their markdown renders literally")

    def check_links(self, path, rel):
        text = strip_code(path.read_text(encoding="utf-8"))
        for m in re.finditer(r"\[[^\]]*\]\(([^)\s]+)\)", text):
            target = m.group(1)
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            frag = target.split("#")[0]
            if not frag:
                continue
            if not (path.parent / frag).resolve().exists():
                self.bad(rel, f"relative link does not resolve: {target}")

    # --- workspace-wide checks -------------------------------------------

    def run(self):
        lessons_dir = self.root / "lessons"
        ref_dir = self.root / "reference"
        if not lessons_dir.is_dir():
            self.bad(self.root.name, "has no lessons/ directory")
            return
        self.sheets = sorted(p.name for p in ref_dir.glob("*.md")) if ref_dir.is_dir() else []

        for path in sorted(lessons_dir.glob("*.md")):
            rel = f"lessons/{path.name}"
            m = re.match(r"^(\d{4})-([a-z0-9-]+)\.md$", path.name)
            if not m:
                self.bad(rel, "filename is not NNNN-kebab-slug.md")
                continue
            info = self.check_lesson(path, rel, int(m.group(1)))
            self.check_prose(path, rel)
            self.check_render(path, rel)
            self.check_links(path, rel)
            if info:
                self.meta[int(m.group(1))] = info

        nums = sorted(self.meta)
        if nums and nums != list(range(1, len(nums) + 1)):
            self.bad("lessons/", f"numbering is not contiguous from 1: {nums}")

        for path in sorted(ref_dir.glob("*.md")) if ref_dir.is_dir() else []:
            rel = f"reference/{path.name}"
            self.check_prose(path, rel)
            self.check_links(path, rel)
            text = path.read_text(encoding="utf-8")
            if not text.startswith("---\n"):
                self.bad(rel, "no front matter")
            if "<details" in text:
                self.bad(rel, "a reference sheet must be scannable, no collapsible blocks")

        for name in ("README.md", "GLOSSARY.md", "RESOURCES.md"):
            path = self.root / name
            if not path.exists():
                self.bad(name, "missing")
                continue
            self.check_prose(path, name)
            self.check_links(path, name)

        notes = self.root / "NOTES.md"
        if notes.exists():
            self.check_notes(notes, "NOTES.md")

        if (self.root / "README.md").exists():
            self.check_readme()
            self.check_arc()
        if (self.root / "GLOSSARY.md").exists():
            self.check_glossary()
        if (self.root / "RESOURCES.md").exists():
            self.check_resources()

    def check_readme(self):
        """Every lesson row must repeat the lesson's own title and description."""
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        for num, info in sorted(self.meta.items()):
            row = re.search(rf"^\| \[{num:04d}\]\(lessons/[^)]+\) \| ([^|]+) \| ([^|]+) \|$",
                            readme, re.M)
            if not row:
                self.bad("README.md", f"no lesson table row for {num:04d}")
                continue
            if row.group(1).strip() != info["title"]:
                self.bad("README.md", f"row {num:04d} titles it {row.group(1).strip()!r}, "
                                      f"lesson says {info['title']!r}")
            if row.group(2).strip() != info["desc"]:
                self.bad("README.md",
                         f"row {num:04d} teaches-column does not match the lesson description")

        for name in self.sheets:
            if f"reference/{name}" not in readme:
                self.bad("README.md", f"reference sheet {name} is not linked")

    def check_arc(self):
        """The arc table ties every lesson to a stage.

        FORMATS.md requires a Lessons column, because a stage nobody's lessons
        reach, or a lesson no stage claims, is how an arc drifts from the
        mission it is supposed to deliver. The column is also the only part of
        "every success bullet leads to a lesson" a tool can check: whether the
        prose of a bullet is delivered by the lessons of its stage stays a
        reviewer's call, but a lesson outside every stage is a fact.
        """
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        m = re.search(r"^## The arc\n(.*?)(?=^## )", readme, re.S | re.M)
        if not m:
            self.bad("README.md", "no '## The arc' section")
            return
        rows = [[c.strip() for c in line.strip().strip("|").split("|")]
                for line in m.group(1).splitlines() if line.strip().startswith("|")]
        if not rows:
            self.bad("README.md", "the arc section has no stage table")
            return

        header = rows[0]
        if "Lessons" not in header:
            if self.conv["arc_lessons_column"]:
                self.bad("README.md", "the arc table has no Lessons column, so no lesson "
                                      "is tied to a stage (FORMATS.md, README.md rules)")
            return
        col = header.index("Lessons")

        seen, stages = {}, 0
        for row in rows[1:]:
            if not row or set(row[0]) <= set("-: "):
                continue
            stages += 1
            cell = row[col] if col < len(row) else ""
            nums = set()
            for a, b in re.findall(r"(\d{4})\s*to\s*(\d{4})", cell):
                if int(a) > int(b):
                    self.bad("README.md", f"arc stage {row[0]!r} names a backwards "
                                          f"range: {a} to {b}")
                nums |= set(range(int(a), int(b) + 1))
            nums |= {int(n) for n in re.findall(r"(?<!\d)(\d{4})(?!\s*to)", cell)}
            if not nums:
                self.bad("README.md", f"arc stage {row[0]!r} names no lessons")
            for n in nums:
                if n in seen:
                    self.bad("README.md", f"lesson {n:04d} is claimed by two stages: "
                                          f"{seen[n]!r} and {row[0]!r}")
                seen[n] = row[0]

        if not stages:
            self.bad("README.md", "the arc table has no stage rows")
            return
        taught = set(self.meta)
        for n in sorted(taught - set(seen)):
            self.bad("README.md", f"lesson {n:04d} exists but no arc stage covers it")
        for n in sorted(set(seen) - taught):
            self.bad("README.md", f"arc stage {seen[n]!r} names lesson {n:04d}, "
                                  f"which does not exist")

    def check_resources(self):
        """Every RESOURCES.md link entry must carry at least one annotation line.

        FORMATS.md requires it: "a bare link is useless in three months."
        Inserting a new entry immediately before an existing one is enough to
        steal the annotation that followed, leaving the pushed-down entry bare
        (#102). At least one line, not exactly one: a deliberate second line,
        such as a reading-order hint, is an editorial choice, not a defect.
        """
        lines = (self.root / "RESOURCES.md").read_text(encoding="utf-8").split("\n")
        for i, line in enumerate(lines, 1):
            if line.startswith("- [") and not (i < len(lines) and lines[i].startswith("  ")):
                self.bad("RESOURCES.md", f"line {i}: entry has no annotation line")

    def check_glossary(self):
        """Alphabetical, because it is looked up rather than read, and every
        term carries the _Avoid_ line that records the common misuse."""
        gl = (self.root / "GLOSSARY.md").read_text(encoding="utf-8")
        parts = gl.split("## Terms", 1)
        if len(parts) != 2:
            self.bad("GLOSSARY.md", "no '## Terms' section")
            return
        body = parts[1]
        entries = re.findall(r"^\*\*([^*]+)\*\*:$", body, re.M)
        for a, b in zip(entries, entries[1:]):
            if a.lower() > b.lower():
                self.bad("GLOSSARY.md", f"{b!r} is out of alphabetical order after {a!r}")
        for term in entries:
            block = body.split(f"**{term}**:", 1)[1].split("\n\n", 1)[0]
            if "_Avoid_:" not in block:
                self.bad("GLOSSARY.md", f"term {term!r} has no _Avoid_: line")


def main():
    if len(sys.argv) < 2:
        print("Usage: check-workspace.py learning/<domain>/<topic> [more workspaces...]",
              file=sys.stderr)
        return 2

    failed = False
    for arg in sys.argv[1:]:
        ws = Workspace(arg)
        ws.run()
        label = f"{ws.root.name.upper()} WORKSPACE"
        if ws.problems:
            failed = True
            print(f"{label}: {len(ws.problems)} PROBLEM(S)")
            for p in ws.problems:
                print("  -", p)
        else:
            print(f"{label}: NO PROBLEMS "
                  f"({len(ws.meta)} lessons, {len(ws.sheets)} sheets)")
    if _markdown is None:
        print("NOTE: the render check was skipped, because this interpreter has no "
              "`markdown` module. Run with the project virtual environment's python "
              "to check that collapsible blocks actually render.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
