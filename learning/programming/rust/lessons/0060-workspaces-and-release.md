---
title: 60. Workspaces and Release
description: Getting a crate to the point where publishing is one command, and what that command actually does
type: lesson
---

# Lesson 60. Workspaces and Release

**Mission link:** A crate nobody can depend on is not shipped, and the gap between working code and a dependable one is a manifest worth trusting, a package containing exactly what it claims to, and a version number that means what it says.
**Primary source:** [Publishing on crates.io](https://doc.rust-lang.org/cargo/reference/publishing.html)
**Prerequisites:** [Lesson 59](0059-features-and-the-minimum-version.md), [Lesson 20](0020-a-library-callers-can-handle.md)

## Warm-up

1. ▢ Lesson 59 pinned `rust-version` inside `[package]` and warned about placing it after `[dependencies]` instead. What does cargo report then?

<details markdown="1"><summary>Check</summary>

Cargo reports:

```text
error: no matching package named `rust-version` found
```

since the misplaced key now sits inside `[dependencies]`, where cargo reads it as a dependency's name rather than a manifest field. The key is still valid TOML; only its position is wrong.

</details>

2. ▢ Lesson 20 put `src/lib.rs` and `src/main.rs` in one package, so both targets shared one `[dependencies]` table, and the binary side pulled in `anyhow` for `.context`. What does that cost a caller who only wants the library?

<details markdown="1"><summary>Check</summary>

That caller still pulls in `anyhow`, even though nothing they call goes near it, because one package has exactly one dependency list shared by every target it builds. This lesson's workspace instead gives the library and the thin binary separate packages, so the library's manifest names only what parsing needs.

</details>

## Know this

### 1. A workspace for a library and a thin binary

A workspace is a root manifest with no `[package]` of its own, only a `[workspace]` table naming the packages it coordinates, so `logsum` and `logsum-cli` become two ordinary packages sharing one `Cargo.lock` and `target` directory instead of two targets forced to share one dependency list:

```toml
[workspace]
members = ["logsum", "logsum-cli"]

[workspace.package]
version = "0.3.0"
edition = "2024"
rust-version = "1.98"
license = "MIT OR Apache-2.0"
repository = "https://example.com/logsum"

[workspace.dependencies]
logsum = { path = "logsum", version = "0.3.0" }
```

Each member opts in with `field.workspace = true`, and a shared dependency the same way, so `logsum-cli`'s manifest carries only what differs:

```toml
[package]
name = "logsum-cli"
version.workspace = true
edition.workspace = true
rust-version.workspace = true
license.workspace = true
repository.workspace = true

[dependencies]
logsum.workspace = true
```

`cargo build` compiles both members with no further wiring, and the inheritance is not cosmetic: raising `workspace.package.rust-version` to `"1.99.0"` and building again reproduces lesson 59's enforcement through the inherited key, unchanged in wording:

```text
error: rustc 1.98.0 is not supported by the following package:
  logsum@0.3.0 requires rustc 1.99.0
```

The Cargo Book marks both `workspace.package` and `workspace.dependencies` with the same note, `MSRV: Requires 1.64+`, so Cargo 1.64 stabilised inheriting a field and a dependency together, not as two separate releases.

### 2. What ships and what does not

`cargo package --list` prints the file list a package would actually upload, worth reading before it is worth trusting, since the packaged crate is a fresh copy under `target/package`, assembled from `include`, `exclude`, and whatever version control already ignores. Narrowing `logsum`'s `include` to `["src/lib.rs", "README.md"]`, forgetting the `src/parse.rs` that `lib.rs` declares with `mod parse;`, leaves `--list` looking plausible, four files instead of five, and only `cargo package`, compiling the packaged copy as its third step, catches what `--list` did not:

```text
error[E0583]: file not found for module `parse`
 --> src/lib.rs:10:1
   |
10 | mod parse;
   | ^^^^^^^^^^
   |
   = help: to create the module `parse`, create file "src/parse.rs" or "src/parse/mod.rs"

error: could not compile `logsum` (lib) due to 1 previous error
error: failed to verify package tarball
```

The `Compiling` line just before this names the temporary directory under `target/package`; it is cut here, naming only this machine. Restoring the missing path to `include` makes `--list` show all five files again and `cargo package` succeed, which is the point of running it first: a forgotten file fails here, against a throwaway copy, rather than in a build a stranger cannot debug.

### 3. The dry run

`cargo publish --dry-run` performs the same packaging and verification as `cargo package`, then stops one step short of uploading, and a manifest missing every optional field says so plainly. Against a fresh package with no `description`, `license` or `repository`, its packaging paths cut below since each names only this machine:

```text
warning: manifest has no description, license, license-file, documentation, homepage or repository
  |
  = note: see https://doc.rust-lang.org/cargo/reference/manifest.html#package-metadata for more info
   Packaging probe v0.1.0 (...)
    Packaged 4 files, 958B (688B compressed)
   Verifying probe v0.1.0 (...)
   Compiling probe v0.1.0 (...)
   Uploading probe v0.1.0 (...)
warning: aborting upload due to dry run
```

`logsum`, once `workspace.package` had already supplied `license` and `repository`, showed the same warning naming only `description`, gone once `description` was added, and the run against the finished manifest packages, verifies and aborts with no warning at all. That is the whole promise of a dry run: it does real work, packaging and compiling a real copy, and its last line, `warning: aborting upload due to dry run`, guarantees none of that work reaches a network beyond reading the crates.io index it checks names against.

### 4. The manifest fields that are not optional in practice

Two fields are not really optional: `description`, since the Cargo Book states that crates.io requires it, and `license` or `license-file`, for the same reason. A crate with neither cannot be published, and one published with neither would be worse: with no stated licence, nobody has permission to use, modify or redistribute the code, however visible its source is, so `license` is what makes the crate usable by anyone but its author, not paperwork. Cargo reads `license` as an SPDX license expression, `license = "MIT OR Apache-2.0"` being the form most of the ecosystem chose, `OR` meaning a user may pick either. `repository` and `documentation` are plain URLs, one to source, one to rendered documentation, and `readme` names a file, rendered on the crate's page, defaulting to `README.md` if unset and one exists. `keywords` and `categories` are the only two the Cargo Book calls optional outright, worth including for discovery but enforced by nothing. None of these change what the code does; they change whether somebody finds the crate, trusts it, or may legally use it once they have.

### 5. Versioning discipline and what you cannot take back

Choosing the next number is lesson 0057's job, applied here rather than repeated: a breaking change forces a major bump, and nothing here changes that rule. What changes is the point a project may cross it casually. The Semantic Versioning specification puts it plainly: "Major version zero (0.y.z) is for initial development. Anything MAY change at any time. The public API SHOULD NOT be considered stable." It also states "Version 1.0.0 defines the public API." and its FAQ adds "If you have a stable API on which users have come to depend, you should be 1.0.0." A changelog says the same thing in prose, for a person deciding whether to upgrade rather than a resolver deciding whether a build compiles. Once uploaded, the specification is equally blunt: "the contents of that version MUST NOT be modified. Any modifications MUST be released as a new version." That is why `cargo yank --version 1.0.1` exists as a retraction rather than a deletion: "A yank does not delete any code." Its only effect is that no new dependency can be created against the yanked version while every lock file that already named it keeps working. Both commands are quoted from the documentation rather than run, since no version of this project's crate exists on a registry to yank.

### 6. Release as a repeatable procedure

Publishing one command away means every check that could fail has already run somewhere other than a human's memory: the test suite, `cargo package --list` read by eyes at least once, a clean `cargo publish --dry-run`, a documentation build (`cargo doc`) with no broken-link warnings, and lesson 0057's semver check, `cargo semver-checks check-release`, compared against the version actually on the registry. None of these checks are new here; the argument added is for running them the same way every time, in continuous integration rather than by hand, since a dry run and a semver check are exactly the two steps slow enough that a human under pressure skips, which is also when they would have caught something. A workspace sharpens one more edge of the same discipline: `cargo publish --dry-run -p logsum-cli`, run before `logsum` reaches the registry, fails with `error: failed to prepare local package for uploading` and a cause naming `logsum` as missing from the registry searched, since publishing rewrites a path dependency into a registry dependency at the declared version, and a registry that has never seen `logsum` has nothing to rewrite it against. A workspace does not remove publishing order; it just makes two packages easy to forget are still two.

## Practice

1. ▢ A file matched by `.gitignore` sits in a package with no `include` or `exclude`, inside a git repository. Predict whether `cargo package --list` shows it, then predict again with no repository present.

<details markdown="1"><summary>Hint</summary>

`cargo package --list` asks version control, rather than reading `.gitignore` as plain text.

</details>

<details markdown="1"><summary>Check</summary>

Inside a repository, the file is left out with no mention in `include`, since cargo asks git which files it tracks. With no repository, the same `.gitignore` does nothing, and the file appears in the list.

</details>

2. ▢ A colleague argues `logsum-cli`'s manifest should move `description` into `workspace.package` alongside `license`, since both members share so much already. Predict what breaks if they inherit it on both sides.

<details markdown="1"><summary>Check</summary>

Nothing mechanical; both packages still build. What is lost is accuracy: a library and its thin binary do different things, so one shared sentence is either too vague or wrong about one of them, unlike `license`, `repository` and `version`, which are one fact about the whole workspace.

</details>

3. ▢ The project is at `0.3.0` and stage 8 has just added `#[non_exhaustive]` to its public enums and a constructor in place of public struct literals. Predict, from this lesson's semver quotations, whether that alone justifies `1.0.0`.

<details markdown="1"><summary>Check</summary>

They make a future breaking change survive as a minor bump instead of a major one, but say nothing about whether the API is finished, and `1.0.0`'s condition is a public API callers already depend on, a judgement about readiness rather than a count of attributes added. The honest move is another `0.y.z` release until that judgement can be made.

</details>

4. ▢ Predict what `cargo publish --dry-run -p logsum-cli` does before `logsum` has ever been published, given `logsum-cli` depends on it through `workspace.dependencies` with a `version` set, then run it.

<details markdown="1"><summary>Hint</summary>

Publishing rewrites a path dependency into whatever the registry would resolve, not the path itself.

</details>

<details markdown="1"><summary>Check</summary>

It fails while preparing to upload, reporting no package named `logsum` on the registry searched, since a path dependency can only publish once cargo restates it as a registry dependency at the given version, and an unpublished `logsum` leaves nothing to restate it against.

</details>

5. ▢ `readme.workspace = true` and `include = ["src/lib.rs"]` sit in the same member manifest. Predict which directory each path is read from before checking the Cargo Book.

<details markdown="1"><summary>Check</summary>

`readme` resolves relative to the workspace root regardless of inheritance, while `include` and `exclude` resolve relative to the package's own root, so a shared `readme` beside the workspace manifest and a member's `include` naming files under its own `src` read from two different starting points.

</details>

## Real-world reps

- [ ] Turn your `logsum` project into a workspace, with the library and the thin binary as separate members sharing `version`, `edition`, `rust-version` and `license` through `[workspace.package]` and the library through `[workspace.dependencies]`.
- [ ] Run `cargo package --list` against your library, narrow `include` until a needed file is missing, read what fails and where, then restore it and confirm `cargo publish --dry-run` is clean with every field from this lesson filled in.
- [ ] Tomorrow: write down the version number you would publish next and the sentence from lesson 0057's rules that justifies it, without running the command that would actually publish it.

## Going further

- [Workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html): the Cargo Book chapter behind `workspace.package` and `workspace.dependencies`
- [The Manifest Format](https://doc.rust-lang.org/cargo/reference/manifest.html): every field a manifest can carry, including the ones this lesson called not optional
- [cargo-yank(1)](https://doc.rust-lang.org/cargo/commands/cargo-yank.html): the full command reference behind what a yank does and does not do
- [Semantic Versioning 2.0.0](https://semver.org/): the specification behind the version number this lesson asks you to choose
- [Judgment](../reference/judgment.md): the stage 8 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
