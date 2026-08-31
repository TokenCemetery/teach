---
title: 10. Exceptions
description: Asking forgiveness instead of permission, and catching exactly what you can handle
type: lesson
---

# Lesson 10. Exceptions

**Mission link:** Python expects exceptions to carry ordinary control flow, not just disasters. Code written as though they are disasters ends up checking everything twice and swallowing the one failure that mattered.
**Primary source:** [The Python Language Reference, The try statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
**Prerequisites:** [Lesson 4](0004-dicts-and-sets.md), [Lesson 9](0009-generators.md)

## Warm-up

1. ▢ Lesson 4 gave four ways to read a dict key. Which one raises, and which one hides a missing key behind a value that might also be stored?

<details markdown="1"><summary>Check</summary>

`d[key]` raises `KeyError`. `d.get(key)` returns `None`, which is indistinguishable from a key whose stored value is `None`.

</details>

2. ▢ What does `except Exception` fail to catch?

<details markdown="1"><summary>Check</summary>

`KeyboardInterrupt`, `SystemExit` and `GeneratorExit`, which descend from `BaseException` rather than `Exception`. That is deliberate, and this lesson says why it matters.

</details>

## Know this

The idiom has a name in the Python documentation: **EAFP**, easier to ask forgiveness than permission. Try the operation, handle the failure.

```python
# EAFP: one lookup, and the failure is handled where it happens
try:
    port = config["port"]
except KeyError:
    port = 8080
```

The alternative, **LBYL**, looks before it leaps:

```python
if "port" in config:                 # two lookups
    port = config["port"]
else:
    port = 8080
```

LBYL is not wrong, and here `config.get("port", 8080)` beats both. LBYL becomes wrong when the check and the action can disagree: a file that exists when you check and is gone when you open it, a key another thread removes in between. The check buys nothing and reads as though it bought safety.

`try` costs almost nothing when no exception is raised. That is a design decision in the language, and it is what makes EAFP affordable.

### The four clauses, and the one people skip

```python
try:
    data = fetch(url)
except TimeoutError:
    data = cached()
else:
    cache.store(data)                # ran only if fetch succeeded
finally:
    connection.close()               # runs no matter what
```

- `except` handles one class of failure. Several may be listed, and the first matching one wins.
- `else` runs only when the `try` block completed without raising. It exists so that code which must not be protected by the `except` stays out of the `try`. Without it, a `KeyError` raised by `cache.store` would be caught by an `except KeyError` meant for `fetch`.
- `finally` always runs: after success, after a handled exception, after an unhandled one on its way out, and after a `return` or `break` in the `try`.

One sharp edge: a `return` inside `finally` discards whatever the rest of the function was doing, including an exception in flight. It is legal and it is almost always a bug.

### Catch what you can handle, and nothing else

```python
except Exception:                    # too wide: hides typos and logic errors
except:                              # worse: also swallows Ctrl-C
except (KeyError, ValueError):       # a claim you can defend
```

`except Exception: pass` is the single most expensive line in Python code, because the failure it hides is exactly the one nobody expected. Two places where a wide catch is legitimate:

1. A top-level loop that must survive one bad item, and **logs the exception with its traceback** before continuing.
2. A boundary that converts anything into a domain failure, using `raise MyError(...) from exc`.

Both keep the information. The bare `pass` destroys it.

`logging.exception("failed to process %s", item_id)` inside an `except` block records the traceback. `logging.error(str(exc))` records a sentence, and `str` on many exceptions is empty.

### Re-raising, and chaining

```python
try:
    parse(raw)
except ValueError as exc:
    log.warning("bad payload")
    raise                            # same exception, original traceback
```

A bare `raise` inside a handler re-raises what is being handled. `raise exc` also works and resets nothing important, but the bare form states the intent.

When translating one failure into another, say where it came from:

```python
raise ConfigError(f"bad port in {path}") from exc
```

`from exc` sets the cause, and the traceback prints both with "The above exception was the direct cause". Omit it and Python still chains implicitly, with "During handling of the above exception, another exception occurred", which reads as an accident. `from None` suppresses the chain, for when the inner exception is noise.

Since Python 3.11, `exc.add_note("port came from the environment")` attaches context to an exception without wrapping it.

### Your own exceptions

```python
class StoreError(Exception):
    """Base for everything this module raises."""

class ItemMissing(StoreError):
    pass
```

One base class per library or package is the whole pattern. It lets a caller write `except StoreError` and be complete, without knowing the internals, and it lets you add a subclass later without breaking them. Inherit from `Exception`, not `BaseException`. Reuse a built-in when it genuinely fits: `ValueError` for a bad value, `TypeError` for a wrong type, `KeyError` and `LookupError` for a missing entry.

`assert` is not error handling. Assertions are removed when Python runs with `-O`, so validation written as `assert user.is_admin` disappears in exactly the deployment where it mattered. Assert internal invariants; `raise` for anything a caller or a user can cause.

### `contextlib.suppress`

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    path.unlink()
```

Exactly equivalent to `try/except FileNotFoundError: pass`, and better, because the suppression is named and cannot accidentally cover three more statements.

### Several failures at once

Since Python 3.11, an `ExceptionGroup` carries multiple exceptions, and `except*` handles them by type without discarding the rest:

```python
try:
    run_all_tasks()                  # raises ExceptionGroup
except* TimeoutError as eg:
    ...                              # eg holds only the timeouts
except* ValueError as eg:
    ...
```

Where this actually shows up is concurrency, and stage 6 uses it. Know now that a plain `except TimeoutError` does **not** catch a `TimeoutError` inside a group, which is the surprise.

## Practice

1. ▢ Predict the output.

   ```python
   def f():
       try:
           return "try"
       finally:
           print("finally")

   print(f())
   ```

<details markdown="1"><summary>Check</summary>

```text
finally
try
```

The return value is computed, then `finally` runs, then the function actually returns. Had `finally` contained `return "finally"`, that value would have replaced it.

</details>

2. ▢ What is wrong with this, given that `cache.store` can raise `KeyError`?

   ```python
   try:
       data = fetch(url)
       cache.store(data)
   except KeyError:
       data = {}
   ```

<details markdown="1"><summary>Hint</summary>

Which clause exists precisely so that the second statement is not protected by the handler?

</details>

<details markdown="1"><summary>Check</summary>

A `KeyError` from `cache.store` is caught by a handler written for `fetch`, and `data` is silently replaced with `{}` after a successful fetch. The cache failure disappears and the caller gets empty data.

```python
try:
    data = fetch(url)
except KeyError:
    data = {}
else:
    cache.store(data)
```

</details>

3. ▢ Rank these four handlers from most to least defensible, and say what each hides.

   - a) `except Exception: pass`
   - b) `except Exception as exc: log.exception("item %s failed", item.id)`
   - c) `except (KeyError, ValueError) as exc: raise ItemInvalid(item.id) from exc`
   - d) `except: pass`

<details markdown="1"><summary>Check</summary>

**c**, then **b**, then **a**, then **d**.

- c) Names what it expects, converts it into a domain failure, and keeps the cause. Defensible in a signature.
- b) Wide, but keeps everything: acceptable in a loop that must survive one bad item.
- a) Hides typos, `AttributeError` from a rename, and every logic error in the block.
- d) Also swallows `KeyboardInterrupt`, so the process ignores Ctrl-C, and `SystemExit`, so a shutdown request is discarded.

</details>

4. ▢ Rewrite as EAFP, and say what the original version's real defect is.

   ```python
   if os.path.exists(path):
       with open(path) as f:
           return f.read()
   return None
   ```

<details markdown="1"><summary>Check</summary>

```python
try:
    with open(path) as f:
        return f.read()
except FileNotFoundError:
    return None
```

The defect is the race: the file can be removed between the check and the open, so the original still raises the exception it was written to avoid. It also fails to handle the neighbouring cases, since a directory or a permission problem passes `exists` and then raises `IsADirectoryError` or `PermissionError`.

</details>

5. ▢ This library raises `KeyError` from its public API. Why is that a design problem, and what should it raise?

   ```python
   def get_user(user_id):
       return _users[user_id]
   ```

<details markdown="1"><summary>Check</summary>

The caller has to catch `KeyError`, which is indistinguishable from a `KeyError` raised by a bug inside `get_user`, or by their own dict in the same `try` block. It also pins the implementation: switching `_users` to a database changes the exception type and breaks every caller.

```python
class UserMissing(StoreError):
    pass

def get_user(user_id):
    try:
        return _users[user_id]
    except KeyError as exc:
        raise UserMissing(user_id) from exc
```

</details>

6. ▢ A service validates input with `assert amount > 0, "amount must be positive"`. Give the failure mode.

<details markdown="1"><summary>Check</summary>

Run under `-O` (or `PYTHONOPTIMIZE`), assertions are stripped and the check is gone, so a negative amount goes straight through. The message is also an `AssertionError`, which tells a caller nothing about which field was wrong.

```python
if amount <= 0:
    raise ValueError(f"amount must be positive, got {amount}")
```

</details>

## Real-world reps

- [ ] Search code you own for `except Exception` and bare `except`. For each, write one sentence naming what it is meant to catch. Any handler you cannot write that sentence for is a defect, and narrowing it is the fix.
- [ ] Find a `try` block with more than one statement in it, and check whether every statement should be covered by the handler. Move the ones that should not into an `else`.
- [ ] Add a single base exception class to a module you own and make everything it raises inherit from it. Then simplify one caller.
- [ ] Tomorrow: replace one `try/except X: pass` with `contextlib.suppress(X)` and notice how much narrower the suppressed region became.

## Going further

- [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement): the exact rules for `else`, `finally`, and `return` inside them
- [Errors and Exceptions, in the tutorial](https://docs.python.org/3/tutorial/errors.html): the guided version, including chaining
- [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html): the hierarchy, and which built-in to reuse instead of inventing one
- [PEP 654, Exception Groups and `except*`](https://peps.python.org/pep-0654/): the multiple-failure model, needed in stage 6
- [`contextlib.suppress`](https://docs.python.org/3/library/contextlib.html#contextlib.suppress): the named form of a narrow catch
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
