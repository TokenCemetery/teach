---
title: Exceptions and Cleanup
description: The hierarchy, what each clause guarantees, and which built-in to raise
type: reference
---

# Exceptions and Cleanup

Lookup sheet for stage 2. The question it exists to answer: **what should this catch, what should it raise, and what is guaranteed to run on the way out?**

## The hierarchy, top levels

```text
BaseException
├── SystemExit            interpreter shutting down: do not catch
├── KeyboardInterrupt     Ctrl-C: do not catch
├── GeneratorExit         a generator is being closed: do not catch
├── BaseExceptionGroup
└── Exception             everything a program is expected to handle
    ├── ArithmeticError    → ZeroDivisionError, OverflowError
    ├── AssertionError
    ├── AttributeError
    ├── EOFError
    ├── ExceptionGroup
    ├── ImportError        → ModuleNotFoundError
    ├── LookupError        → IndexError, KeyError
    ├── MemoryError
    ├── NameError          → UnboundLocalError
    ├── OSError            → FileNotFoundError, PermissionError,
    │                        IsADirectoryError, TimeoutError, ConnectionError
    ├── RuntimeError       → NotImplementedError, RecursionError
    ├── StopIteration, StopAsyncIteration
    ├── SyntaxError        → IndentationError, TabError
    ├── SystemError
    ├── TypeError
    ├── ValueError         → UnicodeError
    └── Warning
```

`except Exception` catches everything in that lower block and none of the top three. A bare `except:` catches the top three as well, which is why it makes a program ignore Ctrl-C.

`TimeoutError` is an `OSError`. Since Python 3.11, `asyncio.TimeoutError` and `socket.timeout` are aliases of it.

## Which one to raise

| Situation | Raise |
|---|---|
| a value is of the right type and wrong | `ValueError` |
| an argument is the wrong type entirely | `TypeError` |
| a key or index is absent | `KeyError`, `IndexError` |
| an operation is not supported on this subclass | `NotImplementedError` |
| the caller used the object in the wrong order or state | a custom exception, or `RuntimeError` |
| something outside the process failed | let the `OSError` subclass through, or wrap it |
| a domain rule was violated | your own subclass of your own base |

`assert` is not in this table. Assertions are stripped under `-O`, so anything a caller or a user can cause must be an explicit `raise`.

## Your own

```python
class StoreError(Exception):
    """Base for everything this package raises."""

class ItemMissing(StoreError):
    pass
```

One base per package, so callers can be complete with `except StoreError`, and so a new subclass does not break them. Never inherit from `BaseException`.

## Clause guarantees

| Clause | Runs when |
|---|---|
| `except X` | an exception matching `X` was raised in the `try` body; first match wins |
| `else` | the `try` body completed with no exception, and **outside** the handlers' reach |
| `finally` | always: success, handled, unhandled, `return`, `break`, `continue` |

Two sharp edges:

- A `return` inside `finally` discards an exception in flight and whatever the function was returning. Almost always a bug.
- Statements in the `try` body that should not be protected belong in `else`. Otherwise a `KeyError` from the second statement is caught by a handler written for the first.

## Chaining

| Form | Traceback says | Use |
|---|---|---|
| `raise New() from exc` | "direct cause" | translating a failure at a boundary |
| `raise New()` inside a handler | "during handling" | implicit; reads as an accident |
| `raise New() from None` | nothing about the inner one | the inner exception is noise |
| bare `raise` | original exception, original traceback | log or clean up, then let it continue |
| `exc.add_note("...")` | the note, on the original | adding context without wrapping; Python 3.11 |

## Handler review checklist

| Handler | Verdict |
|---|---|
| `except (KeyError, ValueError) as e: raise DomainError(...) from e` | defensible: named, converted, cause kept |
| `except Exception: log.exception(...)` in a per-item loop | acceptable: wide, but keeps everything |
| `except Exception: pass` | hides typos, renames and logic errors |
| `except: pass` | also swallows Ctrl-C and shutdown |
| `except Exception as e: log.error(str(e))` | loses the traceback, and `str` is often empty |

`log.exception(msg, *args)` inside a handler records the traceback. `log.error` does not.

## Cleanup

| Need | Tool |
|---|---|
| a paired operation, one resource | `with manager:` |
| write a manager, the everyday way | `@contextlib.contextmanager` plus `try/finally` around the `yield` |
| entry and exit differ by outcome | a class with `__enter__` / `__exit__` |
| an object with `close` and no `__exit__` | `contextlib.closing(obj)` |
| a narrow, named `except X: pass` | `contextlib.suppress(X)` |
| a count of resources known only at run time | `contextlib.ExitStack` and `enter_context` |
| an optional resource, without duplicating the block | `contextlib.nullcontext(fallback)` |
| capture output from code you cannot change | `contextlib.redirect_stdout` |
| change the working directory and restore it | `contextlib.chdir`, Python 3.11 |

### `__exit__` contract

```python
def __exit__(self, exc_type, exc, tb) -> bool | None:
    ...
```

- All three arguments are `None` on a clean exit.
- **Returning truthy suppresses the exception.** Return `None` unless suppression is the documented purpose.
- Multiple managers on one `with` enter left to right and exit right to left.
- A generator-based manager is single-use. Write a class if it must be re-entered.

## Common messages

| Message | Cause |
|---|---|
| `cannot import name 'x' from partially initialized module` | circular import; the module is still executing |
| `attempted relative import with no known parent package` | a file inside a package run as a script; use `python -m` |
| `generator raised StopIteration` | a bare `next(it)` inside a generator body |
| `FrozenInstanceError` | assigning to a field of a frozen dataclass; use `dataclasses.replace` |
| `dictionary changed size during iteration` | mutating a dict while looping a view |
| an `ExceptionGroup` not caught by `except TimeoutError` | a group needs `except*`, or unwrapping |

## Sources

- [The `try` statement](https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)
- [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html)
- [The `with` statement](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement)
- [`contextlib`](https://docs.python.org/3/library/contextlib.html)
- [PEP 654, Exception Groups and `except*`](https://peps.python.org/pep-0654/)
- [PEP 678, Enriching Exceptions with Notes](https://peps.python.org/pep-0678/)
