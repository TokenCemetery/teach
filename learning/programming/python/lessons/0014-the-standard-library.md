---
title: 14. The Standard Library
description: The modules that delete code you were about to write, and the ones that prevent a dependency
type: lesson
---

# Lesson 14. The Standard Library

**Mission link:** Every dependency is a decision someone will have to maintain. A large share of small dependencies exist because the person reaching for one did not know what already shipped with the interpreter.
**Primary source:** [The Python Standard Library](https://docs.python.org/3/library/index.html)
**Prerequisites:** [Lesson 8](0008-the-iteration-protocol.md), [Lesson 12](0012-dataclasses.md), [Lesson 13](0013-modules-and-packages.md)

## Warm-up

1. ▢ Lesson 12 asked which shape a bundle of data deserves. Which shape holds a fixed, closed set of named values, such as three order states?

<details markdown="1"><summary>Check</summary>

Not a dataclass and not three string constants. `enum.Enum`, covered below.

</details>

2. ▢ What does `print(0.1 + 0.2)` show, and what does that rule out?

<details markdown="1"><summary>Check</summary>

`0.30000000000000004`. Binary floating point cannot represent `0.1`, which rules out `float` for money.

</details>

## Know this

The thesis is one sentence: **search the standard library before adding a dependency, and before writing a loop.** What follows is the recognition set, not a reference. The point is to know a module exists so you can look it up.

| Instead of | Use |
|---|---|
| `os.path.join`, string splitting on `/` | `pathlib.Path` |
| `if k not in d: d[k] = []` | `collections.defaultdict` |
| counting with a dict | `collections.Counter` |
| `list.pop(0)` in a queue | `collections.deque` |
| a module-level `_cache = {}` | `functools.cache` |
| three related string constants | `enum.Enum` |
| `datetime.now()` and hoping | `datetime.now(tz)` with `zoneinfo` |
| `float` for money | `decimal.Decimal` |
| `random` for a token | `secrets` |
| `os.system(f"...")` | `subprocess.run([...])` |
| `print` for diagnostics | `logging` |
| hand-parsing `sys.argv` | `argparse` |
| a hand-written CSV split on commas | `csv` |
| `open(tmp, "w")` with a guessed name | `tempfile` |

### `pathlib`

```python
from pathlib import Path

config = Path("~/.config/app.toml").expanduser()
if config.is_file():
    text = config.read_text(encoding="utf-8")

for path in Path("logs").rglob("*.log"):
    print(path.stem, path.stat().st_size)

out = Path("build") / "report" / "index.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
```

`/` joins, `read_text` and `write_text` remove the two-line `with` for the common case, and `rglob` replaces `os.walk`. Always pass `encoding`, because the default is platform-dependent and a file written on one machine is then unreadable on another.

### `collections`

```python
from collections import defaultdict, Counter, deque

by_country = defaultdict(list)
for order in orders:
    by_country[order.country].append(order)     # no key check

counts = Counter(word.lower() for word in words)
counts.most_common(3)

recent = deque(maxlen=100)                      # drops the oldest, no bookkeeping
```

One trap: reading a missing key from a `defaultdict` **creates** it. `if "FR" in by_country` is safe; `if by_country["FR"]` adds an empty list and grows the dict during a read. `deque` matters because `list.pop(0)` shifts every remaining element, so a queue built on a list is quadratic and a `deque` is not.

### `functools`

```python
from functools import cache, cached_property, partial, wraps

@cache                                # unbounded memoisation, since 3.9
def parse_schema(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
```

`cache` is `lru_cache(maxsize=None)` under a clearer name. Three things to know before using it: arguments must be hashable, nothing is ever evicted, and `parse_schema.cache_clear()` exists and is what tests need. Caching a method caches `self` too, which keeps every instance alive forever; `cached_property` is the per-instance version.

`partial(func, timeout=5)` builds a callable with an argument pre-supplied, which is the readable alternative to a `lambda` in a callback. `@wraps` on a decorator copies the wrapped function's name and docstring, without which tracebacks and help output name your wrapper instead.

### `enum`

```python
from enum import Enum, StrEnum, auto

class State(Enum):
    PENDING = auto()
    SHIPPED = auto()
    CANCELLED = auto()

if order.state is State.SHIPPED:      # identity, and a typo is an AttributeError
    ...
```

Three string constants let `state == "shiped"` be silently false forever. An `Enum` makes that an `AttributeError`, gives the set a name, makes it iterable and countable, and prints as `State.SHIPPED` in a traceback. Compare with `is`, since members are singletons.

`StrEnum`, from Python 3.11, makes members also be real strings, which is what a value stored in a database or sent as JSON usually needs. Without it, use `Enum` with explicit string values and convert at the boundary with `State("shipped")`.

### `datetime` and `zoneinfo`

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

now = datetime.now(timezone.utc)                     # aware
local = now.astimezone(ZoneInfo("Europe/Berlin"))    # aware, correct across DST
```

A `datetime` with no `tzinfo` is **naive**: it names a wall-clock reading with no fact about which clock. Naive and aware objects cannot be compared or subtracted, and the moment two machines are involved, naive values are guesses. Two rules cover most production code: store and compute in UTC, convert to a zone only for display. `datetime.utcnow()` is deprecated since 3.12 precisely because it returns a naive value that looks like UTC; `datetime.now(timezone.utc)` is the replacement. `zoneinfo`, from Python 3.9, reads the system tz database, so daylight-saving transitions are handled instead of approximated by a fixed offset.

### `logging`, in the four lines that matter

```python
import logging
log = logging.getLogger(__name__)     # one logger per module, named by lesson 13

log.info("imported %s orders from %s", count, path)   # lazy formatting
log.exception("import failed")                        # inside an except: adds the traceback
```

Pass the values as arguments rather than formatting them in, so the string is only built if that level is enabled. Do **not** call `basicConfig` in library code: configuring handlers is the application's job, and a library that does it fights whatever the application chose.

### `subprocess`

```python
result = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    capture_output=True, text=True, check=True,
)
commit = result.stdout.strip()
```

A list of arguments needs no quoting and cannot be injected into. `shell=True` with an interpolated string is the injection, and `check=True` is what makes a failure raise instead of being ignored.

### How to search

`docs.python.org` has a module index, and the library reference is organised by problem, not alphabetically. Before writing more than about ten lines of a general-purpose utility, read the section heading that covers it. `csv`, `sqlite3`, `statistics`, `textwrap`, `difflib`, `shutil`, `uuid`, `hashlib`, `hmac`, `ipaddress`, `urllib.parse`, `http.server` and `tomllib` are all in there, and each one is a dependency someone else installed.

## Practice

1. ▢ Rewrite with `pathlib`.

   ```python
   import os
   base = os.path.dirname(os.path.abspath(__file__))
   target = os.path.join(base, "data", "out.json")
   os.makedirs(os.path.dirname(target), exist_ok=True)
   with open(target, "w") as f:
       f.write(payload)
   ```

<details markdown="1"><summary>Check</summary>

```python
from pathlib import Path
target = Path(__file__).resolve().parent / "data" / "out.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(payload, encoding="utf-8")
```

The `encoding` is not a detail added for tidiness: the original inherits the platform default, so the same code writes different bytes on different machines.

</details>

2. ▢ Find the bug.

   ```python
   from collections import defaultdict

   totals = defaultdict(int)
   for order in orders:
       totals[order.country] += order.amount

   if totals["FR"]:
       print("France:", totals["FR"])
   print(len(totals), "countries")
   ```

<details markdown="1"><summary>Hint</summary>

Count the keys before and after the `if`.

</details>

<details markdown="1"><summary>Check</summary>

`totals["FR"]` creates the key with value `0` when France is absent, so the count printed on the last line is one too high, and any later loop over `totals` reports a country with no orders.

Use `if totals.get("FR"):`, or `if "FR" in totals:`. The general rule: a `defaultdict` should be written to with `[]` and read from with `get` or `in`.

</details>

3. ▢ For each pair, say which is right and why.

   - a) `random.choice(alphabet)` or `secrets.choice(alphabet)` for a password-reset token
   - b) `float("19.99")` or `Decimal("19.99")` for a price
   - c) `datetime.now()` or `datetime.now(timezone.utc)` for a record's creation time
   - d) `list.pop(0)` or `deque.popleft()` for a work queue

<details markdown="1"><summary>Check</summary>

- a) `secrets`. `random` is a Mersenne Twister seeded predictably enough that observing output reveals future output. It is documented as unsuitable for security.
- b) `Decimal`, constructed **from a string**. `Decimal(19.99)` inherits the float's error, and `Decimal("19.99")` is exact.
- c) The aware one. The naive value cannot be compared with anything from another machine and does not say which clock it read.
- d) `deque`. `pop(0)` moves every remaining element, so draining a queue of n items costs n squared.

</details>

4. ▢ Replace the string constants, and say what the new version catches.

   ```python
   STATUS_PENDING = "pending"
   STATUS_SHIPPED = "shipped"

   def advance(order):
       if order.status == STATUS_PENDING:
           order.status = STATUS_SHIPPED
   ```

<details markdown="1"><summary>Check</summary>

```python
from enum import StrEnum

class Status(StrEnum):
    PENDING = "pending"
    SHIPPED = "shipped"

def advance(order):
    if order.status is Status.PENDING:
        order.status = Status.SHIPPED
```

What it catches: a misspelled member is an `AttributeError` at the point of the typo, rather than a comparison that is quietly false. The valid set is now enumerable, so a check for an unknown status from the database is possible. `Status("shipped")` raises on an unknown value, which is the boundary check. And a checker in stage 3 can prove a function only ever returns one of the members.

`StrEnum` keeps the members usable as strings, so existing storage and JSON continue to work.

</details>

5. ▢ Why is this logging call worse than it looks, and what does it do inside an `except` block?

   ```python
   log.error("failed to import {} orders: {}".format(count, exc))
   ```

<details markdown="1"><summary>Check</summary>

The string is built unconditionally, even when the level is disabled, and log lines are formatted far more often than they are read. `log.error("failed to import %s orders", count)` defers it.

Inside an `except`, `log.exception("failed to import %s orders", count)` is the right call: it records the traceback. Interpolating `exc` gives one line, often an empty one, since many exceptions have an empty `str`, and discards the stack that would have said where it happened.

</details>

6. ▢ A colleague adds a dependency to flatten nested lists, another to retry a function, and another to parse an ISO timestamp. For each, name what could replace it.

<details markdown="1"><summary>Check</summary>

- Flatten: `itertools.chain.from_iterable`, or the two-clause comprehension from lesson 7.
- Retry: a loop with `time.sleep` is a dozen lines and worth writing once; a dependency here is defensible when backoff, jitter and exception policy all matter, which is the argument to have explicitly.
- Parse an ISO timestamp: `datetime.fromisoformat`, which since 3.11 accepts the full ISO 8601 forms including a trailing `Z`.

The point is not that dependencies are bad. It is that "there is a package for it" is not the same as "this needs a package", and knowing the library is what makes the comparison possible.

</details>

## Real-world reps

- [ ] Open the [module index](https://docs.python.org/3/py-modindex.html) and read the names. Not the pages: the names. Twenty minutes, once, and it changes what you reach for.
- [ ] Take your project's dependency list and, for each small one, spend two minutes finding what in the standard library overlaps it. Keep the ones that survive.
- [ ] Convert one file that uses `os.path` to `pathlib`, and add the `encoding` argument everywhere a file is opened.
- [ ] Replace one group of related string constants with an `Enum` and let the type checker or the tests tell you where the comparisons were wrong.
- [ ] Tomorrow: find a naive `datetime` in code you own and follow it to where it is compared or stored. Decide whether anyone knows which clock it read.

## Going further

- [The Python Standard Library](https://docs.python.org/3/library/index.html): organised by problem, which is how to search it
- [`pathlib`](https://docs.python.org/3/library/pathlib.html), [`collections`](https://docs.python.org/3/library/collections.html), [`functools`](https://docs.python.org/3/library/functools.html), [`enum`](https://docs.python.org/3/library/enum.html): the four with the highest ratio of code deleted to page length
- [`logging` HOWTO](https://docs.python.org/3/howto/logging.html): levels, handlers, and why a library configures nothing
- [`zoneinfo`](https://docs.python.org/3/library/zoneinfo.html): the system time-zone database, and what an aware datetime buys
- [`subprocess`](https://docs.python.org/3/library/subprocess.html): the security notes on `shell=True` are the part to read
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
