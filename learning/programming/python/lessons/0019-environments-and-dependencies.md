---
title: 19. Environments and Dependencies
description: Isolation per project, the difference between a requirement and a lock, and who pins what
type: lesson
---

# Lesson 19. Environments and Dependencies

**Mission link:** "It works on my machine" is almost always a dependency statement. Knowing the difference between a requirement and a lock is what makes an install reproducible on a machine you have never seen.
**Primary source:** [Python Packaging User Guide](https://packaging.python.org/en/latest/)
**Prerequisites:** [Lesson 13](0013-modules-and-packages.md)

## Warm-up

1. ▢ Lesson 13: why does `python -m shop.orders` work from one directory and fail from another?

<details markdown="1"><summary>Check</summary>

`sys.path[0]` is the current working directory, so the package is importable only from the directory that contains it. Installing the project removes the question, which is where this lesson ends up.

</details>

2. ▢ Two projects on one machine need version 1 and version 3 of the same library. Where does that break?

<details markdown="1"><summary>Check</summary>

An interpreter has one `site-packages`, so the second install replaces the first. That is what a virtual environment exists to prevent.

</details>

## Know this

### A virtual environment is a directory with its own `site-packages`

```bash
python -m venv .venv
```

```python
sys.prefix != sys.base_prefix        # True inside the environment
```

That is nearly all it is. The `.venv` directory holds an interpreter (usually a symlink), a `site-packages`, and scripts. Activating it only puts its `bin` directory first on `PATH`, which is why `.venv/bin/python script.py` works identically without activating anything, and why "activation did not work" is almost always a shell problem rather than a Python one.

Three rules follow:

- One environment per project, in the project, named `.venv` by convention.
- Never commit it. It contains compiled artefacts for one platform and one interpreter version.
- Never install into the interpreter that came with the operating system. The system depends on it.

### A requirement is not a lock

This is the distinction the rest of the lesson rests on.

```toml
[project]
name = "shop"
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.27",
    "sqlalchemy>=2.0,<3",
]
```

That is an **abstract requirement**: a range of acceptable versions, stated in `pyproject.toml`, which is the standard defined by PEP 621. It says what the code needs.

A **lock file** is the concrete answer a resolver computed: every package including transitive ones, one exact version each, with hashes.

```toml
[[packages]]
name = "anyio"
version = "4.14.2"
index = "https://pypi.org/simple"
wheels = [{ url = "...", hashes = { sha256 = "9f505dda..." } }]
```

Both are needed and they answer different questions. The requirement travels with your package to other people's resolvers. The lock reproduces one exact install, today, on a build machine.

`pip freeze > requirements.txt` is neither: it is a snapshot of whatever is currently installed, including packages you no longer use, with no distinction between what you asked for and what came along.

### Version specifiers

| Written | Means |
|---|---|
| `>=2.1` | at least this, no upper limit |
| `>=2.1,<3` | at least this, below the next major |
| `~=2.1.3` | compatible release: `>=2.1.3,<2.2.0` |
| `~=2.1` | `>=2.1,<3.0` |
| `==2.1.3` | exactly this |
| `==2.1.*` | any patch of 2.1 |
| `!=2.1.4` | anything but this release |
| `httpx[http2]` | with an optional feature set, called an extra |
| `tomli; python_version < "3.11"` | only on interpreters that need it, called a marker |

### Who pins, and who constrains

| | Application or service | Library |
|---|---|---|
| `pyproject.toml` | ranges | ranges, as wide as honestly supportable |
| lock file | committed | not published |
| upper bounds | fine | only with a known incompatibility |
| CI installs from | the lock | the ranges, and ideally the oldest and newest |

The asymmetry matters. An application controls its own deployment, so pinning exactly is what makes a deploy reproducible and a rollback possible. A library is installed **alongside** other people's dependencies, and every upper bound it declares can make some combination unresolvable. `<3` on a library that has not seen version 3 yet is a guess that costs your users a fork.

### Dependency groups, for what is not a dependency

```toml
[dependency-groups]
dev = [
    "pytest>=8",
    "mypy>=1.11",
]
```

Test and lint tools are not runtime dependencies, and they must not appear in `[project.dependencies]`, or every consumer installs them. PEP 735 groups are the current standard for this and are not published with the package. The older spelling, an extra named `dev`, is still common and does get published.

### Install your own project too

```bash
pip install -e .
```

An **editable install** puts your project on the path while still reading the files in place, so edits take effect without reinstalling. It is what makes `import shop` work from anywhere, which is lesson 13's problem solved at the root, and it is why the `src/` layout is worth adopting: with sources under `src/`, an accidental import can only succeed if the package is genuinely installed, so the tests exercise what users will get.

```text
shop/
├── pyproject.toml
├── src/
│   └── shop/
│       ├── __init__.py
│       └── orders.py
└── tests/
    └── test_orders.py
```

### Reproducing an install

Three ingredients, and missing any one of them makes "it works here" luck:

1. The interpreter version, declared in `requires-python` and fixed in CI.
2. The lock file, committed.
3. An install command that **fails** rather than resolving, when the lock does not match the requirements. Every tool has a flag for this; use it in CI.

`pylock.toml` is worth knowing by name: PEP 751 standardises the lock format, so a lock is no longer tied to the tool that produced it, and most tools can now export to it.

### The tools, and what survives them

`pip` and `venv` ship with Python and always work. `uv`, `poetry` and `pdm` combine environment creation, resolution, locking and running into one command, and are faster and stricter about reproducibility.

```bash
uv init             # pyproject.toml, src layout, .python-version
uv add httpx        # edits pyproject.toml, updates the lock, installs
uv add --dev pytest # into [dependency-groups]
uv sync             # make the environment match the lock exactly
uv run pytest       # run inside that environment without activating it
```

Tools change. `pyproject.toml`, the specifier syntax, `requires-python`, editable installs and the lock-against-requirement distinction are standards, and they are what transfers when the tool you learned is replaced.

## Practice

1. ▢ Which of these belongs in `[project.dependencies]`?

   - a) `httpx`, used by the code that runs in production
   - b) `pytest`, used by the tests
   - c) `mypy`, run in CI
   - d) `tomli`, needed only on Python 3.10 and older

<details markdown="1"><summary>Check</summary>

**a** and **d**. The `tomli` line needs a marker: `tomli; python_version < "3.11"`, since `tomllib` is in the standard library from 3.11.

**b** and **c** belong in `[dependency-groups]`. Putting them in `[project.dependencies]` means every user of your package installs a test runner and a type checker.

</details>

2. ▢ A library declares `dependencies = ["requests==2.31.0"]`. Name three things that go wrong.

<details markdown="1"><summary>Hint</summary>

Think about a second library in the same environment.

</details>

<details markdown="1"><summary>Check</summary>

- Any other package requiring a different `requests` makes the environment unresolvable, and the user cannot fix it without forking one of the two.
- Security fixes in `requests` cannot be installed without a new release of your library.
- It claims knowledge you do not have: that 2.31.1 breaks you, which nobody has tested.

`>=2.28` is the honest version, with an upper bound added only when a specific release is known to break.

</details>

3. ▢ Match each to what it actually is.

   - a) `pyproject.toml` `[project.dependencies]`
   - b) `uv.lock` or `pylock.toml`
   - c) output of `pip freeze`
   - d) `.venv/`

<details markdown="1"><summary>Check</summary>

- a) Abstract requirements: ranges, published with the package, read by other people's resolvers.
- b) A concrete resolution: exact versions including transitive ones, with hashes. Committed for an application, not published for a library.
- c) A snapshot of one environment's current contents. Not a lock, because it does not distinguish direct from transitive, and not a requirement, because it has no ranges.
- d) A local, disposable directory of installed artefacts for one platform and interpreter. Never committed.

</details>

4. ▢ CI installs dependencies and the build passes. The same commit fails in production a week later, with an error from a library nobody changed. Where is the defect?

<details markdown="1"><summary>Hint</summary>

Ask what exact versions the two installs used, and what decided them.

</details>

<details markdown="1"><summary>Check</summary>

The install resolved ranges instead of reading a lock, so CI got the versions available that day and production got the versions available a week later. The build was never reproducible; it happened to be identical.

Fix: commit the lock, install from it, and use the flag that makes a stale lock a failure rather than a silent re-resolution. Then upgrading is a commit that changes the lock file and runs the tests, which is exactly what it should be.

</details>

5. ▢ Why does the `src/` layout catch a packaging bug that a flat layout hides?

<details markdown="1"><summary>Check</summary>

With a flat layout, the package directory sits next to the tests, so `sys.path[0]` finds it whether or not it was installed, and whether or not the packaging configuration includes it. Tests pass against the working tree.

With sources under `src/`, nothing is importable from the project root, so the tests can only run against an installed copy. A file missing from the built distribution therefore fails locally, rather than in the first user's install.

</details>

6. ▢ A colleague commits `.venv/` "so the build machine does not have to install anything". Give the reasons this fails.

<details markdown="1"><summary>Check</summary>

The environment contains platform-specific compiled artefacts and absolute paths, so it will not run on a different operating system, architecture, or interpreter version. It is large and changes on every install, which makes the history unreadable. And it records no intent: a reviewer cannot see which packages were asked for, only what ended up on disk.

The thing that achieves the intended goal is the lock file, which is small, text, reviewable, and reproduces the same install on any supported platform.

</details>

## Real-world reps

- [ ] Create an environment for a project you have, install nothing globally for a week, and note what breaks. Whatever breaks was an undeclared dependency.
- [ ] Take a project with a `requirements.txt` produced by `pip freeze` and split it: direct requirements with ranges into `pyproject.toml`, everything else into a lock. Compare the length of the two lists.
- [ ] Install your own project editable and delete the `sys.path` manipulation or the `python file.py` habit that was standing in for it.
- [ ] Read your CI install step and answer whether a dependency released this morning could change the result. If it could, fix that.
- [ ] Tomorrow: look up one dependency in your lock that you did not choose, and find which direct dependency requires it.

## Going further

- [Python Packaging User Guide](https://packaging.python.org/en/latest/): the current standards, kept up to date as they change
- [Dependency specifiers](https://packaging.python.org/en/latest/specifications/dependency-specifiers/): the exact grammar for versions, extras and markers
- [PEP 621, Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/): the `[project]` table
- [PEP 735, Dependency Groups](https://peps.python.org/pep-0735/): development dependencies that are not published
- [PEP 751, A file format to record Python dependencies](https://peps.python.org/pep-0751/): the standard lock format
- [`venv`](https://docs.python.org/3/library/venv.html): what the directory contains and what activation does
- [uv documentation](https://docs.astral.sh/uv/): one current tool for all of the above
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
