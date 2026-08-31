---
title: 43. Reading the Source
description: Getting the answer from the standard library and the PEPs when the documentation stops
type: lesson
---

# Lesson 43. Reading the Source

**Mission link:** The mission ends with reading the standard library and the PEPs for answers. That is a specific skill: knowing which of the four sources answers which kind of question, and being willing to open the one that does.
**Primary source:** [Python Developer's Guide](https://devguide.python.org/)
**Prerequisites:** [Lesson 13](0013-modules-and-packages.md), [Lesson 23](0023-properties-and-descriptors.md), [Lesson 27](0027-metaclasses-and-why-not.md)

## Warm-up

1. ▢ Lesson 23 called one documentation page the best in the standard library on its subject. Which, and why?

<details markdown="1"><summary>Check</summary>

The Descriptor HowTo Guide, because it builds properties, methods and `classmethod` up from the protocol rather than listing them.

</details>

2. ▢ You need to know whether `dict.get` is faster than `try/except KeyError`. Which source answers it?

<details markdown="1"><summary>Check</summary>

None of them. That is a measurement, per lesson 39. Knowing which questions the documents cannot answer is half of this lesson.

</details>

## Know this

### Four sources, four kinds of question

| Question | Source |
|---|---|
| what does this function do | the library reference |
| what does the language guarantee | the language reference |
| why is it like this | the PEP, and the discussion thread |
| what does it actually do in this case | the source |
| when did this change | What's New, and the version-status page |
| how fast is it | a measurement |

Reaching for the wrong one is the usual reason a search takes an hour. "Why can I not subclass this" is a PEP question; "does `dict` preserve order" is a language-reference question, and the answer is a guarantee since 3.7 rather than an implementation detail, which only the reference tells you.

### Reading the library source

It is Python, it is on your disk, and it is more readable than most people expect:

```python
import collections, inspect
print(inspect.getsourcefile(collections.Counter))
print(inspect.getsource(collections.Counter.most_common))
```

Three entry points, in order of convenience: `inspect.getsource` for a function or class, `inspect.getsourcefile` to open the whole module, and the CPython repository on the web when the implementation is in C.

Where the source is the only answer:

- **Exact edge behaviour.** What `str.split` does with consecutive separators, in the case the docs summarise.
- **What a wrapper actually calls.** Three layers of a framework, and the profile said one of them was slow.
- **Whether something is a coincidence.** `re.findall` compiling per call, from lesson 39's profile, is visible in `re/__init__.py` in four lines.
- **Reading a good implementation.** `contextlib`, `dataclasses`, `functools` and `pathlib` are short, modern, heavily reviewed Python, and reading `contextlib.ExitStack` teaches more about context managers than any article.

Two warnings. A leading underscore in the standard library means the same as in your code, so building on `_thread` or `re._compile` is building on something that can change in a patch release. And what you read is CPython's implementation, not the language: `sys.intern` behaviour, small-integer caching, and dict ordering before 3.7 were all implementation details people built on and regretted.

### Reading a PEP

A PEP has a shape, and reading it in this order saves time:

1. **The header**: status, the Python version it landed in, and what it replaced. `Final` means shipped; `Accepted` means agreed but perhaps not released; `Rejected` and `Withdrawn` PEPs are often the most useful, because they say why the obvious idea does not work.
2. **Abstract and Motivation**: the problem. This is the part that answers "why".
3. **Rationale** and **Rejected Ideas**: the alternatives and why they lost, which is where the answer to your objection usually is.
4. **Specification**: the details. Read this last, because the reference documentation is easier for the same content.

Four worth reading in full, and each explains a decision that shapes daily code: [PEP 8](https://peps.python.org/pep-0008/), [PEP 20](https://peps.python.org/pep-0020/), [PEP 484](https://peps.python.org/pep-0484/) on gradual typing, and [PEP 703](https://peps.python.org/pep-0703/) on the interpreter lock.

The archive matters too. Typing and packaging decisions are argued out in public on the Python Discourse, and when no document explains a shape, the thread usually does.

### Version questions

```text
docs.python.org/3/whatsnew/          per release: additions, deprecations, removals
devguide.python.org/versions/        which releases are supported, and until when
```

Any claim beginning "you can now" or "you can no longer" needs one of those two pages, and this arc has three examples of why: annotations became lazy in 3.14, `fork` stopped being the default start method in 3.14, and `warnings.deprecated` arrived in 3.13. Each would have been wrong if recalled rather than checked.

The version-status page also answers the question a library maintainer actually has, which is which interpreters `requires-python` should allow.

### The documentation has a structure worth learning

| Section | Contains |
|---|---|
| Tutorial | the guided introduction, best for a first pass on a built-in type |
| Library Reference | every module, organised by problem |
| Language Reference | syntax and semantics, including scoping and the data model |
| HOWTOs | descriptors, logging, sorting, regex, free threading: short and excellent |
| Glossary | one-line canonical definitions, useful for pinning a term |

The HOWTOs are the most under-read part. Five of them are the best available treatment of their topic, and they are all under an hour.

### A worked example

Question: does `functools.cache` on a method leak memory?

- The library reference says `cache` is `lru_cache(maxsize=None)` and notes that caching a method keeps `self` alive. That is the answer, and the wording is easy to miss.
- The source, `functools.py`, shows the cache is a dict keyed by the arguments **including** `self`, which makes the mechanism concrete: the dict lives on the function, which lives on the class, so every instance ever passed is reachable forever.
- The `cached_property` documentation gives the per-instance alternative, and mentions the `__slots__` incompatibility, which the source explains in one line.

Three sources, four minutes, and the answer is not just yes but why, which is what makes it transferable to the next caching question.

## Practice

1. ▢ Which source answers each?

   - a) Does `dict` preserve insertion order, and is that guaranteed?
   - b) Why does `list` not have a `find` method?
   - c) What exactly does `str.split()` with no argument do to leading whitespace?
   - d) When did `except*` become available?
   - e) Is a set comprehension faster than `set()` of a generator?

<details markdown="1"><summary>Check</summary>

- a) The language reference, and the answer is that it is a guarantee since 3.7, having been an implementation detail in 3.6. The distinction is exactly what the reference exists for.
- b) A PEP or a mailing-list thread, since it is a design question. `index` raises and `in` tests, and the rationale is that a `find` returning `-1` invites unchecked results.
- c) The library reference first, and the source if the edge case is not covered. Verified: `"  a  b  ".split()` gives `['a', 'b']`, while `"  a  b  ".split(" ")` gives `['', '', 'a', '', 'b', '', '']`. No argument treats runs of whitespace as one separator and discards leading and trailing; an explicit separator does neither.
- d) What's New, or the PEP header: PEP 654, Python 3.11.
- e) A measurement. No document answers it, and the answer changes between releases.

</details>

2. ▢ You find `re._compile` used in a codebase. What is the objection?

<details markdown="1"><summary>Hint</summary>

What does the underscore mean, and what does that imply about the next patch release?

</details>

<details markdown="1"><summary>Check</summary>

The underscore means private, in the standard library exactly as in your own code. It has no compatibility promise, so it can change signature or disappear in a patch release of CPython, and the failure appears on an interpreter upgrade in code nobody touched.

The practical response is to ask what it was for. Usually the answer is "caching compiled patterns", and the public answer is to compile once at module level, which lesson 39 measured as a real win anyway.

</details>

3. ▢ Read the shape: a PEP is marked `Rejected`. Why might it be the most useful one to read?

<details markdown="1"><summary>Check</summary>

Because it contains the argument. A rejected PEP proposed the obvious thing, and its rejection notice explains why the obvious thing does not work, which is precisely the question you have when you wonder why the language lacks a feature.

It also prevents wasted effort: proposals to add multiline lambdas, to change the scoping rules, and to make `self` implicit have all been made and answered in detail, and reading the answer is faster than rediscovering it.

</details>

4. ▢ A colleague says reading the standard library source is for compiler people. Answer them.

<details markdown="1"><summary>Check</summary>

Most of it is ordinary Python on their own disk, and `inspect.getsource` prints it without leaving the interpreter. On CPython 3.14, `contextlib` is 814 lines and is the clearest available explanation of context managers; `functools` is 1,165 and `pathlib` 1,307; `dataclasses` is 1,813 and shows exactly what the decorator generates. Those are afternoon-sized, not compiler-sized.

Then the practical argument: three questions in this arc were answered only by the source or by running it. Whether `re` recompiles per call, whether caching a method holds `self`, and what `__slots__` does to `cached_property` are all one file away and absent from any tutorial.

The concession: the parts implemented in C genuinely are a different skill, and reading them is rarely necessary. Knowing which parts are Python is the useful half.

</details>

5. ▢ Design your own answer procedure for "can I do X in Python", in four steps.

<details markdown="1"><summary>Check</summary>

One reasonable version:

1. **Library reference** for the module involved, searching by problem rather than by name. Most questions end here.
2. **What's New and the version-status page** if the answer depends on a release, which any "can I now" question does.
3. **The source**, via `inspect.getsource`, when the reference summarises the case you care about.
4. **The PEP, then the Discourse thread**, when the question is why rather than what.

With a measurement instead of all four when the question is about speed, and a small experiment in the interpreter when it is about behaviour. The habit worth building is that step zero is always "which kind of question is this", because that choice is what makes the search short.

</details>

6. ▢ Three claims in this arc changed after being checked. What does that suggest about your own knowledge of Python?

<details markdown="1"><summary>Check</summary>

That the version-sensitive parts expire quietly. Annotations became lazily evaluated, the default process start method changed, and a set of micro-optimisations that were true measurably stopped being true. None of those announced themselves; each was found by running the code or reading What's New.

The practical conclusion is a habit rather than an attitude: for any claim about performance, atomicity, or a default, check it on the interpreter you are targeting before you rely on it or teach it. And treat confident advice from before the last two releases, including your own, as a hypothesis.

</details>

## Real-world reps

- [ ] Read `contextlib.py` end to end. It is 814 lines, and it makes lesson 11 permanent.
- [ ] Use `inspect.getsource` on three functions you use daily and read what they actually do.
- [ ] Read one HOWTO from the documentation in full. Descriptors, sorting, and logging are the three with the highest return.
- [ ] Read the Rejected Ideas section of one PEP whose feature you have wished for.
- [ ] Check one version-sensitive belief you hold against What's New. Expect to be wrong about at least one.
- [ ] Tomorrow: find a leading-underscore name from a dependency or the standard library used in your codebase, and replace it with something public.

## Going further

- [Python Developer's Guide](https://devguide.python.org/): how CPython is developed, and the version-status page
- [The Python Language Reference](https://docs.python.org/3/reference/index.html): what the language guarantees, as opposed to what CPython does
- [Python HOWTOs](https://docs.python.org/3/howto/index.html): the under-read section, including descriptors, sorting and free threading
- [PEP index](https://peps.python.org/): including the rejected ones
- [Python Discourse](https://discuss.python.org/): where typing and packaging decisions are argued out
- [`inspect`](https://docs.python.org/3/library/inspect.html): reading the source of anything without leaving the interpreter
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
