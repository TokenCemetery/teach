---
title: Project and Packaging
description: One pyproject.toml annotated, the specifier grammar, and the checks before publishing
type: reference
---

# Project and Packaging

Lookup sheet for stage 3. The question it exists to answer: **what goes in `pyproject.toml`, and what proves the artefact works?**

## Layout

```text
shop/
├── pyproject.toml          all configuration, one file
├── uv.lock                 committed for an application, not for a library
├── README.md               becomes the project page
├── .git-blame-ignore-revs  the reformatting commit
├── src/
│   └── shop/
│       ├── __init__.py
│       ├── py.typed        required if the package ships annotations
│       └── cli.py
└── tests/
```

`src/` means nothing is importable without installing, so tests exercise what users get.

## `pyproject.toml`, annotated

```toml
[build-system]                          # PEP 517/518: who builds the wheel
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]                               # PEP 621: the published metadata
name = "shopkit-demo"                   # normalised; need not match the import name
version = "0.2.0"                       # PEP 440; permanent once uploaded
description = "One line, shown in search results"
readme = "README.md"
requires-python = ">=3.11"              # stops installs on interpreters you cannot run on
license = "MIT"
dependencies = [                        # abstract ranges, read by other resolvers
    "httpx>=0.27",
    "tomli; python_version < '3.11'",
]

[project.scripts]                       # becomes a command on PATH
shopkit = "shopkit.cli:main"

[project.urls]
Homepage = "https://example.invalid/shopkit"

[dependency-groups]                     # PEP 735: not published
dev = ["pytest>=8", "mypy>=1.11", "ruff>=0.6"]

[tool.mypy]
strict = true

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "S", "PTH", "RET"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]
```

## Specifiers

| Written | Means |
|---|---|
| `>=2.1` | at least this |
| `>=2.1,<3` | at least this, below the next major |
| `~=2.1.3` | `>=2.1.3,<2.2.0` |
| `~=2.1` | `>=2.1,<3.0` |
| `==2.1.3` | exactly this |
| `==2.1.*` | any patch of 2.1 |
| `!=2.1.4` | anything but that release |
| `httpx[http2]` | with an extra |
| `x; python_version < "3.11"` | with a marker |

## Requirement against lock

| | `[project.dependencies]` | lock file |
|---|---|---|
| contains | direct dependencies, as ranges | everything, exact, with hashes |
| audience | other people's resolvers | your build machine |
| application | ranges | committed |
| library | ranges, as wide as honest | not published |

`pip freeze` output is neither: a snapshot of one environment with no ranges and no direction.

Upper bounds in a library make combinations unresolvable for users. Add one only for a known incompatibility.

`pylock.toml` (PEP 751) is the standard lock format, so a lock is no longer tied to one tool.

## Environments

```bash
python -m venv .venv          # a directory with its own site-packages
.venv/bin/python -m pip ...   # activation is only PATH; the path always works
pip install -e .              # editable: your project importable from anywhere
```

- One per project, named `.venv`, never committed.
- Never install into the interpreter the operating system uses.
- `sys.prefix != sys.base_prefix` is how code can tell it is inside one.

## Artefacts

| | sdist `.tar.gz` | wheel `.whl` |
|---|---|---|
| contents | source tree plus metadata | files as installed |
| install | builds on the user's machine | unpack and copy |
| publish | yes | yes |

```text
shopkit_demo-0.2.0-py3-none-any.whl
     name    version  py abi platform
```

Wheel contents for a pure-Python package:

```text
shopkit/__init__.py
shopkit/cli.py
shopkit/py.typed
shopkit_demo-0.2.0.dist-info/METADATA
shopkit_demo-0.2.0.dist-info/RECORD
shopkit_demo-0.2.0.dist-info/WHEEL
shopkit_demo-0.2.0.dist-info/entry_points.txt
```

## Before publishing

1. Build both artefacts from a clean tree.
2. List the wheel's contents. Anything missing is the bug.
3. Install the wheel into an **empty** environment; import it and run the entry point.
4. Run the test suite against the installed package, not the source tree.
5. Confirm `py.typed` is present, if the package is annotated.
6. Upload to TestPyPI, install from there.
7. Upload to the real index.

Use trusted publishing rather than a long-lived token. A version cannot be reused after upload; yanking hides it from new resolutions while keeping existing pins working.

## Reading the version at run time

```python
from importlib.metadata import version
version("shopkit-demo")            # the distribution name, not the import name
```

One source of truth. A `__version__` constant plus a number in `pyproject.toml` is two.

## Command map

| Task | `uv` | standard tools |
|---|---|---|
| create an environment | `uv venv` | `python -m venv .venv` |
| add a dependency | `uv add httpx` | edit `pyproject.toml`, then `pip install -e .` |
| add a dev dependency | `uv add --dev pytest` | edit `[dependency-groups]` |
| match the environment to the lock | `uv sync` | `pip install -r <exported requirements>` |
| run inside the environment | `uv run pytest` | `.venv/bin/pytest` |
| build | `uv build` | `python -m build` |
| publish | `uv publish` | `twine upload dist/*` |

Tools change; `pyproject.toml`, the specifier grammar, editable installs, wheels and the lock distinction are standards.

## Sources

- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
- [Writing your `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [Dependency specifiers](https://packaging.python.org/en/latest/specifications/dependency-specifiers/)
- [PEP 621](https://peps.python.org/pep-0621/), [PEP 735](https://peps.python.org/pep-0735/), [PEP 751](https://peps.python.org/pep-0751/), [PEP 517](https://peps.python.org/pep-0517/), [PEP 561](https://peps.python.org/pep-0561/)
- [Trusted publishing](https://docs.pypi.org/trusted-publishers/)
