---
title: Resources
description: "Trusted sources for Bash"
type: resources
---

# Bash Resources

## Knowledge

- [Docs: "Shell Command Language", POSIX.1-2017, The Open Group](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
  The authoritative specification for `sh`: quoting, expansion, exit status, and exactly what's portable versus bash-specific. Use for: settling what POSIX `sh` actually guarantees, rather than what happens to work in one shell.
- [Docs: "Bash Reference Manual", GNU](https://www.gnu.org/software/bash/manual/bash.html)
  The official reference for bash-specific behavior beyond POSIX `sh`: shell functions, `local`, parameter expansion, arrays, and job control. Use for: the exact rule for a bash-only feature, once POSIX's own specification doesn't cover it.
- [Site: "Bash Pitfalls", Greg's Wiki](https://mywiki.wooledge.org/BashPitfalls)
  A long, concrete catalog of shell scripts that look correct and aren't, each with the specific input that breaks it and why. Use for: recognizing a failure mode by its shape, before writing the code that has it.
- [Article: "Use the Unofficial Bash Strict Mode (Unless You Looove Debugging)", Aaron Maxwell](http://redsymbol.net/articles/unofficial-bash-strict-mode/)
  Explains `set -euo pipefail` and `IFS` hardening: what each flag changes about how a script fails, and the specific bugs each one prevents. Use for: the baseline defensive setup for any script meant to survive production.
- [Tool: ShellCheck](https://www.shellcheck.net/)
  A static analyzer that catches quoting mistakes, unset-variable use, and other common shell bugs before the script ever runs, with an explanation for each warning. Use for: checking a script for the failure modes this mission covers, rather than relying on memory alone.
- [Site: "Shell Style Guide", Google](https://google.github.io/styleguide/shellguide.html)
  A practical style guide that also states explicitly when a script has grown complex enough that it should be rewritten in a real scripting language instead. Use for: the "knowing when to stop" half of the mission, stated as a concrete, opinionated rule rather than a vague feeling.
- [Docs: "A Sed and Awk Micro-Primer", Advanced Bash-Scripting Guide, TLDP](https://tldp.org/LDP/abs/html/sedawk.html)
  A brief introduction to `sed` and `awk` specifically in the context of shell scripts that call them, not as standalone languages of their own. Use for: recognizing the shape of task each tool actually fits, without treating either as a topic to learn in full.
- [Tool: shfmt](https://github.com/mvdan/sh)
  An automatic formatter for shell scripts, normalizing indentation and layout to a consistent style. Use for: the formatting half of the checks a script should pass before shipping, distinct from ShellCheck's correctness checks.
- [Tool: bats-core](https://github.com/bats-core/bats-core)
  A TAP-compliant testing framework for Bash, with a `run` helper that captures a command's exit status and output for assertions. Use for: testing a script's actual behavior, not just its static correctness.
