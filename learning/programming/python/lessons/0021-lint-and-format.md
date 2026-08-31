---
title: 21. Lint and Format
description: Ending the style argument, and the rule families that find real defects
type: lesson
---

# Lesson 21. Lint and Format

**Mission link:** A formatter removes an entire category of review comment. A linter finds the defects a type checker cannot see. Together they are the cheapest quality mechanism available, and the only cost is deciding the configuration once.
**Primary source:** [Ruff documentation](https://docs.astral.sh/ruff/)
**Prerequisites:** [Lesson 16](0016-making-a-checker-useful.md), [Lesson 19](0019-environments-and-dependencies.md)

## Warm-up

1. ▢ Lesson 6: what is wrong with `def collect(items, seen=[])`?

<details markdown="1"><summary>Check</summary>

The default is evaluated once, so every call sharing it accumulates. A linter reports this as `B006`, which is the point of this lesson.

</details>

2. ▢ Lesson 16: name one defect a type checker cannot find.

<details markdown="1"><summary>Check</summary>

Anything not about types: an unused variable, a `try/except/pass`, a mutable default, a comparison that is always true. Three tools, three jobs.

</details>

## Know this

### A formatter is not a linter

A **formatter** rewrites layout deterministically. Input:

```python
x = {  "a":1,
  "b" :2 }
def f( a,b ):
  return a+b
```

Output, from any formatter run by anyone:

```python
x = {"a": 1, "b": 2}


def f(a, b):
    return a + b
```

The value is not beauty, it is that layout stops being a decision. Nobody reviews indentation, diffs contain only real changes, and the argument about line breaks is settled by a tool that does not care. Adopt one, accept its opinions, and do not configure it beyond line length.

One migration detail: reformatting an existing codebase is one enormous commit. Do it alone, in its own commit, and record that commit's hash in a `.git-blame-ignore-revs` file so `git blame` keeps pointing at whoever wrote the logic.

A **linter** finds defects. On this file:

```python
import os, sys
from typing import List

def collect(items, seen = [], mode = "read"):
    result = []
    for i in range(len(items)):
        result.append(items[i])
    try:
        return result[0]
    except Exception:
        pass
    unused = 1
    return undefined_name
```

it reports, among others:

```text
E401    Multiple imports on one line
F401    `os` imported but unused
UP035   `typing.List` is deprecated, use `list` instead
I001    Import block is un-sorted or un-formatted
B006    Do not use mutable data structures for argument defaults
PERF401 Use a list comprehension to create a transformed list
S110    `try`-`except`-`pass` detected, consider logging the exception
BLE001  Do not catch blind exception: `Exception`
F841    Local variable `unused` is assigned to but never used
F821    Undefined name `undefined_name`
```

`F821` is the one to notice. An undefined name is a `NameError` waiting for the branch to be taken, found here without running anything.

### The rule families worth knowing

| Prefix | Family | Finds |
|---|---|---|
| `F` | pyflakes | real defects: undefined names, unused imports and variables |
| `E`, `W` | pycodestyle | layout, mostly handled by the formatter |
| `I` | isort | import order and grouping |
| `B` | bugbear | traps: mutable defaults, calls in defaults, loop-variable capture |
| `UP` | pyupgrade | constructs superseded by your minimum Python version |
| `SIM` | simplify | conditionals and comprehensions that collapse |
| `RET` | return | unnecessary `else` after `return`, inconsistent returns |
| `S` | bandit | security: `shell=True`, `try/except/pass`, weak hashes, `assert` in production paths |
| `PTH` | use-pathlib | `os.path` calls with a `pathlib` equivalent |
| `TRY`, `BLE` | exception rules | blind catches, `raise` inside `try`, missing `from` |
| `ANN` | annotations | missing annotations, overlapping with a checker |
| `D` | pydocstyle | docstring presence and shape |
| `PL` | pylint subset | too many arguments, branches, statements |

`F` and `B` are the two that repay their configuration cost immediately. `UP` is the cheapest modernisation available: it rewrites the old spellings from lesson 15 automatically.

### Configure it explicitly

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "S", "PTH", "RET"]
ignore = ["E501"]                       # the formatter owns line length

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]                    # assert is the point in a test
```

Two decisions in that block matter more than the rule list.

`target-version` tells the linter which Python you support, so `UP` does not rewrite code into syntax your users' interpreters cannot parse.

And the selection is **explicit**. Default rule sets change between tool versions, so a project relying on the default gets new findings from an upgrade it did not ask for. Write the list down.

Do not `select = ["ALL"]`. On the file above it produces twenty-one findings including a missing copyright notice and two missing docstrings, and it enables rules that contradict each other:

```text
warning: `incorrect-blank-line-before-class` (D203) and `no-blank-line-before-class` (D211)
         are incompatible. Ignoring `incorrect-blank-line-before-class`.
```

A rule set nobody chose is a rule set everyone silences.

### Fixing, and silencing

```bash
ruff check --fix .              # apply the safe fixes
ruff format .
```

Safe fixes preserve behaviour. Unsafe ones, behind a separate flag, might not: removing an unused import can break code relying on the import's side effect, and the tool is right to make you ask.

When a rule is wrong for one line:

```python
subprocess.run(cmd, shell=True)  # noqa: S602
```

Always with the code, for the same reason as `# type: ignore[code]` in lesson 16: a bare `noqa` also hides the finding that appears on that line next year. Ruff can report unused `noqa` comments, which keeps the set honest.

If a rule is wrong for the project, put it in `ignore` with a comment saying why. A repeated `noqa` is a configuration decision that has not been made yet.

### Three layers, three jobs

| Tool | Catches | Misses |
|---|---|---|
| formatter | nothing; it prevents arguments | everything |
| linter | undefined names, unused code, known traps, insecure calls | whether the types line up |
| type checker | type mismatches, `None` handling, exhaustiveness | whether the logic is right |
| tests | whether the logic is right | what nobody wrote a test for |

Each layer is cheap only because the others exist. A linter's value comes from being fast enough to run on save; a checker's from being able to reason about the whole program; a test's from executing it.

### Where it runs

Locally on save, as a pre-commit hook, and in CI. The hook makes the feedback immediate; **CI is the authority**, because a hook can be skipped and a local install can be a different version. Both should read the same configuration file, and the CI job should pin the tool version, so a release of the linter does not turn into a red build on an unrelated pull request.

Tools change here faster than anywhere else in the arc. Ruff currently covers the linting, import sorting and formatting that several separate tools used to do; before it, that was pycodestyle, pyflakes, isort and black. The rule families and their reasons are the durable part.

## Practice

1. ▢ For each finding, say whether a type checker would also have caught it.

   - a) `F821 Undefined name 'undefined_name'`
   - b) `B006 Do not use mutable data structures for argument defaults`
   - c) `F401 'os' imported but unused`
   - d) `arg-type: Argument 1 has incompatible type "str"; expected "int"`

<details markdown="1"><summary>Check</summary>

- a) Yes, both find it. It is a name-resolution error, not a style question.
- b) No. The types are correct; the semantics are the trap.
- c) A checker may warn with the right flags, and it is squarely a linter's job.
- d) Only the checker. A linter does not know what `find` expects.

The overlap is real and partial, which is why both run.

</details>

2. ▢ Why is `select = ["ALL"]` a bad default?

<details markdown="1"><summary>Hint</summary>

Consider what happens on the second day, and what the tool itself says about some combinations.

</details>

<details markdown="1"><summary>Check</summary>

It enables rules nobody chose, including opinionated families like mandatory docstrings and copyright headers, and rules that directly contradict each other, which the tool reports as a warning while ignoring one of them.

The outcome is predictable: hundreds of findings, a wall of `ignore` entries added without discussion, and a team that stops reading the linter's output. A selected list of six to ten families that the team can defend is worth more than every rule with half of them muted.

</details>

3. ▢ What is wrong with each?

   - a) `x = eval(user_input)  # noqa`
   - b) `except Exception:  # noqa: BLE001` in a per-item loop that logs the exception
   - c) `# ruff: noqa` at the top of a file
   - d) `ignore = ["E501"]` in the config

<details markdown="1"><summary>Check</summary>

- a) A bare `noqa` on a genuinely dangerous line, hiding both the security rule and anything else reported there later. If it must stay, name the code and write the reason.
- b) Defensible. The rule's objection is a blind catch that loses information, and logging the exception answers it. A comment saying so is what makes it reviewable.
- c) Turns off linting for a whole file, permanently and invisibly. Use per-file-ignores in the config, where it is a visible decision.
- d) Correct and deliberate: the formatter owns line length, so the linter reporting it is noise.

</details>

4. ▢ A team adopts a formatter and the first commit changes 400 files. What do they do about `git blame`?

<details markdown="1"><summary>Check</summary>

Make the reformatting its own commit, touching nothing else, then record its hash in `.git-blame-ignore-revs`. Git skips those revisions when assigning blame, so the history keeps pointing at whoever wrote each line.

The other half of the answer is to do it before the branches that are in flight, not after, because rebasing feature work across a whole-repo reformat is the actual cost.

</details>

5. ▢ Lint passes locally and fails in CI on the same commit. Give three causes.

<details markdown="1"><summary>Check</summary>

- Different tool versions: the developer's install is older or newer, and the rule set changed.
- Different configuration: the hook reads one file, CI passes flags of its own.
- Different file selection: locally only changed files were checked, CI checks everything, and an old file has always been failing.

The fixes are the same in each case: pin the tool version in the project's dependency group, have both read `pyproject.toml`, and make CI the authority.

</details>

6. ▢ A colleague argues linting is bikeshedding and the team should spend the time on tests. Answer them.

<details markdown="1"><summary>Check</summary>

Agree with half of it. Style rules are bikeshedding, and that is exactly why a formatter should decide them with no human involved.

The other half is wrong about what a linter is. `F821` is an undefined name, `B006` is a shared mutable default, `S602` is a shell injection, `F841` is code that does nothing: these are defects, found in under a second across the whole repository, with no test to write. A test suite finds the defects you thought of; a linter finds the ones with a known name.

The honest concession: a linter configured with rules nobody chose does become bikeshedding, and it earns the complaint.

</details>

## Real-world reps

- [ ] Run a linter over a project you know with `select = ["F", "B"]` and read every finding. These two families are almost entirely real defects.
- [ ] Add a formatter in its own commit, then add the hash to `.git-blame-ignore-revs` and confirm `git blame` still attributes a line correctly.
- [ ] Turn on `UP` with the right `target-version` and let it modernise one file automatically. Read the diff before committing it.
- [ ] Find every bare `# noqa` in code you own and give each a code, or delete it. Then enable the check for unused ones.
- [ ] Tomorrow: put the linter and the checker in CI as separate steps, so a red build says which of the two failed.

## Going further

- [Ruff rules](https://docs.astral.sh/ruff/rules/): every rule with its rationale, which doubles as a catalogue of Python mistakes
- [Ruff configuration](https://docs.astral.sh/ruff/configuration/): `select`, `ignore`, per-file ignores, and the formatter's options
- [Ruff formatter](https://docs.astral.sh/ruff/formatter/): what it changes, and the deviations from black
- [PEP 8](https://peps.python.org/pep-0008/): the conventions the rules encode, including the parts about when to break them
- [pre-commit](https://pre-commit.com/): running the same tools locally as in CI
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
