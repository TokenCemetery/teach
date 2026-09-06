---
title: Resources
description: "Trusted sources for Bash"
type: resources
---

# Bash Resources

## Knowledge

- [Docs: "Shell Command Language", POSIX.1-2017, The Open Group](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
  The authoritative specification for `sh`: quoting, expansion, exit status, and exactly what's portable versus bash-specific. Use for: settling what POSIX `sh` actually guarantees, rather than what happens to work in one shell.
- [Site: "Bash Pitfalls", Greg's Wiki](https://mywiki.wooledge.org/BashPitfalls)
  A long, concrete catalog of shell scripts that look correct and aren't, each with the specific input that breaks it and why. Use for: recognizing a failure mode by its shape, before writing the code that has it.
- [Article: "Use the Unofficial Bash Strict Mode (Unless You Looove Debugging)", Aaron Maxwell](http://redsymbol.net/articles/unofficial-bash-strict-mode/)
  Explains `set -euo pipefail` and `IFS` hardening: what each flag changes about how a script fails, and the specific bugs each one prevents. Use for: the baseline defensive setup for any script meant to survive production.
- [Tool: ShellCheck](https://www.shellcheck.net/)
  A static analyzer that catches quoting mistakes, unset-variable use, and other common shell bugs before the script ever runs, with an explanation for each warning. Use for: checking a script for the failure modes this mission covers, rather than relying on memory alone.
- [Site: "Shell Style Guide", Google](https://google.github.io/styleguide/shellguide.html)
  A practical style guide that also states explicitly when a script has grown complex enough that it should be rewritten in a real scripting language instead. Use for: the "knowing when to stop" half of the mission, stated as a concrete, opinionated rule rather than a vague feeling.

## Gaps

- No source yet specifically on `awk`/`sed` usage patterns within a larger shell script (as opposed to `awk`/`sed` as topics of their own, which are explicitly out of scope); worth closing once lesson design reaches a script that needs one of them incidentally.
