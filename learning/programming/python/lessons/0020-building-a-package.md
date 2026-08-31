---
title: 20. Building a Package
description: What a wheel is, what the metadata has to say, and proving the artefact installs
type: lesson
---

# Lesson 20. Building a Package

**Mission link:** The mission says someone else can install the result on a machine it was not written on. That is a specific artefact with specific metadata, and the only way to know it works is to install it into an empty environment and run it.
**Primary source:** [Python Packaging User Guide, Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
**Prerequisites:** [Lesson 13](0013-modules-and-packages.md), [Lesson 19](0019-environments-and-dependencies.md)

## Warm-up

1. ▢ Lesson 19: why does the `src/` layout catch a packaging bug a flat layout hides?

<details markdown="1"><summary>Check</summary>

Nothing under `src/` is importable from the project root, so tests can only run against an installed copy. A file missing from the built distribution fails locally instead of in a user's install.

</details>

2. ▢ What does `pip install some-package` actually do to your environment?

<details markdown="1"><summary>Check</summary>

Usually it downloads a wheel and unpacks it into `site-packages`, running no code from the package. This lesson is about producing that file.

</details>

## Know this

### Two artefacts

| | Source distribution (`.tar.gz`) | Wheel (`.whl`) |
|---|---|---|
| contents | your source tree plus metadata | the files as they land in `site-packages` |
| install | requires a build step on the user's machine | unpack and copy |
| runs your build code on the user's machine | yes | no |
| needed for | building on unusual platforms, and by distributors | every ordinary install |

Publish both. The wheel is what almost everyone gets; the sdist is what makes the package buildable on a platform you never tested and is what lets a distribution rebuild it from source.

A wheel filename is structured, and reading one tells you what it supports:

```text
shopkit_demo-0.2.0-py3-none-any.whl
     name    version  python abi platform
```

`py3-none-any` is a pure-Python wheel: any interpreter from Python 3, no compiled extension, any platform. A package with C code instead has many wheels, one per interpreter and platform.

### The build system declaration

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

PEP 517 and 518 separate the two halves: a **frontend** (`pip`, `build`, `uv`) knows how to ask for a wheel, and a **backend** knows how to make one. The frontend installs the backend in an isolated environment first, which is why this table has to be declarative.

Any backend works. `setuptools` is the incumbent and the one every legacy project uses, `hatchling` and `flit` are simpler for pure-Python packages, `uv_build` is fast and newer, `poetry-core` comes with poetry, `maturin` and `scikit-build-core` exist for compiled code. The choice affects one table in `pyproject.toml` and nothing your users see.

### Metadata that has consequences

```toml
[project]
name = "shopkit-demo"
version = "0.2.0"
description = "Demo package for a lesson"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []
license = "MIT"

[project.scripts]
shopkit = "shopkit.cli:main"

[project.urls]
Homepage = "https://example.invalid/shopkit"
```

- **`name`** is normalised: `Shop_Kit` and `shop-kit` are the same project, and the distribution name need not match the import name. `shopkit-demo` above installs a package imported as `shopkit`, which is common and is worth stating in the readme.
- **`version`** must be a PEP 440 version. Once uploaded, a version is permanent: it can be yanked but not replaced, so `0.2.0` is spent the moment it is published.
- **`requires-python`** is what stops an install on an interpreter your code cannot run on. Without it, users on an old interpreter get a syntax error instead of a resolver message.
- **`readme`** becomes the project page. It is the only documentation most people read.
- **`[project.scripts]`** generates a command on the user's `PATH`, pointing at `module:function`. In the built wheel it becomes:

  ```text
  [console_scripts]
  shopkit = shopkit.cli:main
  ```

- **`py.typed`**, an empty file inside the package, is what tells a checker your annotations are real. Without it, PEP 561 says tools must ignore them, so a fully annotated library gives its users nothing.

### One source of truth for the version

```python
from importlib.metadata import version

def get_version() -> str:
    return version("shopkit-demo")
```

The version lives in the metadata, and the code reads it from there. The alternative, a `__version__` string in the package plus a number in `pyproject.toml`, is two places that drift. Note the argument is the **distribution** name, not the import name.

### Build it, then prove it

```bash
uv build            # or: python -m build
```

```text
dist/shopkit_demo-0.2.0-py3-none-any.whl
dist/shopkit_demo-0.2.0.tar.gz
```

Look inside. It takes ten seconds and catches the most common defect, which is a file that is not there:

```text
shopkit/__init__.py
shopkit/cli.py
shopkit/py.typed
shopkit_demo-0.2.0.dist-info/METADATA
shopkit_demo-0.2.0.dist-info/RECORD
shopkit_demo-0.2.0.dist-info/WHEEL
shopkit_demo-0.2.0.dist-info/entry_points.txt
```

Then install the artefact into an empty environment and use it:

```bash
uv venv .fresh
uv pip install --python .fresh/bin/python dist/*.whl
.fresh/bin/python -c "import shopkit; print(shopkit.get_version())"
.fresh/bin/shopkit
```

This is the only check that means anything, because it exercises what a user gets rather than what your working tree contains. Data files, templates, a missing `__init__.py`, a subpackage the backend did not find: all of them pass every test in the repository and fail here.

### Publishing

1. Build both artefacts from a clean tree.
2. Upload to TestPyPI, install from there into an empty environment.
3. Upload to PyPI.

For the credentials, prefer **trusted publishing**: the index verifies a short-lived token from your CI provider, so there is no long-lived API token to leak. A token stored in CI is the fallback, and a token on a laptop is the thing to avoid.

Two facts about the index worth knowing before the first upload. A version cannot be reused, even after deletion, so a botched `1.0.0` costs you `1.0.1`. And yanking a release hides it from new resolutions while keeping it installable for anything that already pinned it, which is the correct response to publishing something broken.

## Practice

1. ▢ The build produces an sdist and then fails on the wheel. The layout is `src/shopkit/` and the project name is `shopkit-demo`. What is missing?

<details markdown="1"><summary>Hint</summary>

The backend has to be told which directory is the package when it cannot guess from the name.

</details>

<details markdown="1"><summary>Check</summary>

The backend infers the package directory from the distribution name, and `shopkit-demo` does not match `src/shopkit`. It needs an explicit statement, which for hatchling is:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/shopkit"]
```

The sdist succeeded because it just archives the source tree. This is the general shape of packaging bugs: the sdist is fine and the wheel is wrong or empty.

</details>

2. ▢ A library is fully annotated, published, and its users' checkers report `Any` for everything it returns. What is missing?

<details markdown="1"><summary>Check</summary>

The `py.typed` marker file inside the package, and the packaging configuration that includes it in the wheel.

PEP 561 requires the marker; without it, a checker must ignore the annotations, because it cannot tell whether they were ever verified. Check the built wheel, not the source tree: the file existing in the repository and missing from the artefact is the usual failure.

</details>

3. ▢ Which of these are permanent once published?

   - a) The version number
   - b) The readme shown on the project page
   - c) The declared dependencies of that release
   - d) The availability of the release to new installs

<details markdown="1"><summary>Check</summary>

- a) Permanent. It cannot be reused, even if the release is deleted.
- b) Part of the artefact's metadata, so fixing it needs a new release.
- c) Also in the artefact. A wrong dependency range is fixed by releasing again, not by editing.
- d) Changeable: yanking removes it from new resolutions while keeping it installable for existing pins.

The practical consequence: rehearse on TestPyPI, and treat the first upload of a version as final.

</details>

4. ▢ Tests pass, coverage is high, and the first user reports `ModuleNotFoundError: No module named 'shopkit.templates'`. What check was skipped?

<details markdown="1"><summary>Check</summary>

Installing the built wheel into an empty environment and importing from it. The tests ran against the working tree, where `shopkit/templates/` exists on disk; the wheel does not contain it, because the directory has no `__init__.py`, or the backend was not told to include non-Python files.

The repeatable version of this check belongs in CI: build, install the wheel in a fresh environment, run the test suite against the installed package rather than the source directory.

</details>

5. ▢ Why does the code read its version from `importlib.metadata` instead of a `__version__` constant?

<details markdown="1"><summary>Check</summary>

Because there is then one place the version lives. A constant in the package plus a number in `pyproject.toml` are two, and they drift on exactly the release where you were in a hurry: the artefact says `0.3.0` and the log line says `0.2.0`.

The reverse arrangement also exists, where the backend reads the version out of the source file, and is equally valid. What is not valid is maintaining both by hand.

</details>

6. ▢ A colleague publishes with a long-lived API token stored in their shell profile. Name the concrete risks and the alternative.

<details markdown="1"><summary>Check</summary>

The token is on a laptop, in plain text, with permission to publish any version of the project. It leaks through a stolen machine, a synced dotfiles repository, a shell history, or a compromised dependency that reads environment variables. Nobody can tell a legitimate upload from an illegitimate one afterwards, and a malicious release is installed automatically by everyone downstream.

Trusted publishing removes the token: the index accepts a short-lived credential issued to a specific CI workflow in a specific repository, so there is nothing durable to steal. If a token must exist, it belongs in the CI provider's secret store, scoped to the single project.

</details>

## Real-world reps

- [ ] Build a package from a project you have, then list the contents of the wheel. Whatever you expected to see and did not is the bug.
- [ ] Install your own wheel into an empty environment and run the tests against the installed copy rather than the source tree.
- [ ] Add `[project.scripts]` for something you currently run with `python -m`, and check the generated `entry_points.txt` in the wheel.
- [ ] If you publish an annotated library, verify `py.typed` is inside the built artefact.
- [ ] Tomorrow: publish something to TestPyPI end to end. The first upload is where every metadata mistake surfaces, and doing it on the real index is how projects burn a version number.

## Going further

- [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/): the end-to-end tutorial, kept current
- [Writing your `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/): every field in `[project]` and what it affects
- [PEP 517](https://peps.python.org/pep-0517/) and [PEP 518](https://peps.python.org/pep-0518/): the frontend and backend split
- [PEP 440, Version Identification](https://peps.python.org/pep-0440/): what counts as a version, including pre-releases
- [PEP 561, Distributing and Packaging Type Information](https://peps.python.org/pep-0561/): the `py.typed` marker
- [Trusted publishing](https://docs.pypi.org/trusted-publishers/): publishing without a long-lived token
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
