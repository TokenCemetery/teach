---
title: 39. Tasks and the Send Bound
description: What spawning an async task demands of the future you hand it, and why an async trait method will not satisfy it
type: lesson
---

# Lesson 39. Tasks and the Send Bound

**Mission link:** A `tokio::spawn` call is the only construct in this stage that can put two futures on two different threads at once, and it is guarded by exactly the bound lesson 29 required of `thread::spawn`, for the same reason.
**Primary source:** [tokio::task::spawn](https://docs.rs/tokio/1.53.1/tokio/task/fn.spawn.html)
**Prerequisites:** [Lesson 34](0034-send-and-sync.md), [Lesson 38](0038-wakers-executors-and-runtimes.md)

## Warm-up

1. ▢ Lesson 38 showed that a future only makes progress when an executor polls it again, and that one poll loop can only poll one future at any instant. If a single threaded executor holds two futures at once, what does "both make progress" mean for it, and what would it take for them to run at literally the same instant rather than in turns?

<details markdown="1"><summary>Check</summary>

For one poll loop, "both make progress" can only mean interleaved turns: whichever future its waker just woke gets polled to its next await point, then control returns to the loop for the other. Running at literally the same instant needs a second poll loop on its own thread.

</details>

2. ▢ Lesson 29 required a closure handed to `thread::spawn` to satisfy `Send + 'static`. Which of those two bounds is about a value's fields being unsafe to move to another thread, and which is about how long the value may keep referring to something it borrowed?

<details markdown="1"><summary>Check</summary>

`Send` is the fields question: lesson 34 showed it derived structurally, so a value built from a part that lacks `Send` loses it too. `'static` is the borrowing question: the spawned thread might outlive the frame that started it, so nothing it holds may depend on that frame still existing.

</details>

## Know this

### A task runs whether or not you await it

`tokio::spawn` takes a future and hands back a `JoinHandle<T>`, itself a `Future<Output = Result<T, JoinError>>`, so getting the value back is just awaiting the handle. The documentation says the future "will start running in the background immediately when spawn is called, even if you don't await the returned JoinHandle", while also guaranteeing "spawn will not synchronously poll the task being spawned": scheduled straight away, but never run inline.

```rust
let handle = tokio::spawn(async {
    println!("task body ran");
});
println!("spawn returned, handle not yet awaited");
sleep(Duration::from_millis(50)).await;
handle.await.unwrap();
```

Three of three runs printed `spawn returned, handle not yet awaited` before `task body ran`, confirming spawn does not run inline, and `task body ran` still printed well before the handle was ever awaited. Compare a future that is merely created and never spawned or awaited at all:

```rust
let _future = async {
    println!("bare future body ran");
};
println!("future dropped without being awaited");
sleep(Duration::from_millis(50)).await;
```

Three of three runs printed only `future dropped without being awaited`: `bare future body ran` never printed, even after the surrounding task yielded at its own await point. A bare future is inert until polled, and dropping it silently discards the work; a task is registered with the runtime the moment `spawn` is called and needs nobody to await its handle to make progress.

### Three shapes, only one of which can cross threads

Sequential `.await`s, `tokio::join!`, and two spawned tasks read as three phrasings of one idea, but only the third can put the two operations on different threads.

```rust
async fn work(n: u64) -> u64 {
    println!("work({n}) running on {:?}", std::thread::current().id());
    sleep(Duration::from_millis(20)).await;
    n * 10
}

let total = match mode {
    "sequential" => work(1).await + work(2).await,
    "join" => { let (a, b) = tokio::join!(work(1), work(2)); a + b }
    "spawn" => {
        let h1 = tokio::spawn(work(1));
        let h2 = tokio::spawn(work(2));
        h1.await.unwrap() + h2.await.unwrap()
    }
    _ => unreachable!(),
};
```

On a runtime started with `#[tokio::main(flavor = "multi_thread", worker_threads = 4)]`, five of five sequential runs and five of five join runs printed both `work` lines on the same thread id, while five of five spawn runs printed two different thread ids; all three printed `total = 30` every time. Sequential and `join!` both run their futures inside the one task that is the calling code's own async body, so the runtime has exactly one place to run it, `join!` only interleaving the two futures' polls rather than giving either its own task; `tokio::spawn` hands each future to the runtime as an independent task the scheduler may place on any worker thread, the only shape of the three that can answer yes to "did this run on more than one thread".

### The bound is spawn's whole contract

`tokio::spawn`'s signature is `pub fn spawn<F>(future: F) -> JoinHandle<F::Output> where F: Future + Send + 'static, F::Output: Send + 'static`, the same two bounds lesson 29 named for `thread::spawn` and for the same reason: the task may move to a different worker thread than the one that called `spawn`, and it may outlive the frame that spawned it. Holding a value that is not `Send` across an await inside a spawned future reproduces this, using `Rc` rather than lesson 41's `MutexGuard`:

```rust
async fn touch(label: Rc<String>) {
    sleep(Duration::from_millis(10)).await;
    println!("{label}");
}

let label = Rc::new(String::from("hi"));
tokio::spawn(touch(label)).await.unwrap();
```

```text
error: future cannot be sent between threads safely
   --> src/main.rs:13:18
    |
 13 |     tokio::spawn(touch(label)).await.unwrap();
    |                  ^^^^^^^^^^^^ future returned by `touch` is not `Send`
    |
    = help: within `impl Future<Output = ()>`, the trait `Send` is not implemented for `Rc<String>`
note: future is not `Send` as this value is used across an await
   --> src/main.rs:6:38
    |
  5 | async fn touch(label: Rc<String>) {
    |                ----- has type `Rc<String>` which is not `Send`
  6 |     sleep(Duration::from_millis(10)).await;
    |                                      ^^^^^ await occurs here, with `label` maybe used later
note: required by a bound in `tokio::spawn`
    |
174 |     pub fn spawn<F>(future: F) -> JoinHandle<F::Output>
    |            ----- required by a bound in this function
175 |     where
176 |         F: Future + Send + 'static,
    |                     ^^^^ required by this bound in `spawn`
```

The line naming the absolute path to tokio's own source inside the crate registry has been cut from the second `note`. The diagnostic is not measuring whether `Rc<String>` appears in the function, but whether it is still alive across the `.await`: confining its use to before the suspension point compiles, unchanged type and all.

```rust
tokio::spawn(async {
    {
        let label = Rc::new(String::from("hi"));
        println!("{label}");
    }
    sleep(Duration::from_millis(10)).await;
    println!("done");
})
.await
.unwrap();
```

This printed `hi` then `done` with no diagnostic: the `Rc` is dropped well before the `.await`, so nothing not `Send` is held across a suspension. Choosing `Arc<String>` over `Rc<String>` from the start also compiles unchanged, the fix when a value genuinely needs to survive a thread hop rather than merely being read once first.

### Why there is no scoped spawn

Stage 5's `thread::scope`, lesson 30's organising idea, let a thread borrow a local because the scope guaranteed the borrow could not outlive it. Tokio's task module offers no equivalent, only `spawn`, `id` and `try_id`, because a task might still be running after the function that spawned it returns, exactly what `'static` rules out. A future that would have borrowed a local under stage 5's design now has to move an owned value in or share it behind an `Arc`, paying lesson 30's cloning cost and, if the data is mutated, lesson 33's locking cost too.

### async fn in a trait, and why async-trait still exists

An `async fn` in a trait compiles, and calling it directly compiles too, since the concrete implementation's future type is fully known at the call site.

```rust
trait LineSource {
    async fn next_line(&mut self) -> Option<String>;
}

struct Fixed(Vec<String>);

impl LineSource for Fixed {
    async fn next_line(&mut self) -> Option<String> {
        self.0.pop()
    }
}

let mut src = Fixed(vec!["a".into(), "b".into()]);
while let Some(line) = src.next_line().await {
    println!("{line}");
}
```

This printed `b` then `a`, the vector's own pop order. Trouble starts once the caller is generic over the trait rather than holding a concrete `Fixed`, exactly the shape a summariser reading several kinds of source needs:

```rust
fn spawn_next<S: LineSource + Send + 'static>(mut src: S) -> tokio::task::JoinHandle<Option<String>> {
    tokio::spawn(async move { src.next_line().await })
}
```

```text
error: future cannot be sent between threads safely
   --> src/main.rs:6:5
    |
  6 |     tokio::spawn(async move { src.next_line().await })
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ future created by async block is not `Send`
    |
    = help: within `{async block@src/main.rs:6:18: 6:28}`, the trait `Send` is not implemented for `impl Future<Output = Option<String>>`
note: future is not `Send` as it awaits another future which is not `Send`
   --> src/main.rs:6:31
    |
  6 |     tokio::spawn(async move { src.next_line().await })
    |                               ^^^^^^^^^^^^^^^ await occurs here on type `impl Future<Output = Option<String>>`, which is not `Send`
note: required by a bound in `tokio::spawn`
    |
174 |     pub fn spawn<F>(future: F) -> JoinHandle<F::Output>
    |            ----- required by a bound in this function
175 |     where
176 |         F: Future + Send + 'static,
    |                     ^^^^ required by this bound in `spawn`
help: `Send` can be made part of the associated future's guarantees for all implementations of `LineSource::next_line`
    |
  2 -     async fn next_line(&mut self) -> Option<String>;
  2 +     fn next_line(&mut self) -> impl std::future::Future<Output = Option<String>> + Send;
    |
```

Again the crate registry's path is cut from the `note`. `S: Send` says nothing about the future `S::next_line` returns, because `async fn` in a trait desugars to an opaque associated future per implementation, and that opacity does not inherit `Send` through a generic bound. The `help` is the compiler rewriting the trait's own declaration into return-position `impl Trait` with an explicit `+ Send`, which fixes `spawn_next` once the trait's definer applies it; proving `Send` this way for every implementation is what the `async-trait` crate papers over instead, rewriting the method to return a boxed, pinned future whose `Send`-ness is named once on the trait, at the cost of an allocation per call. `async fn` and return-position `impl Trait` in traits stabilised in release 1.75, and `async-trait` is still downloaded about 137 million times a quarter for exactly this gap.

### A task that panics

Awaiting a `JoinHandle` for a task that panics gives back an `Err(JoinError)` rather than unwinding into the caller, and `JoinError` carries more than lesson 29's `thread::spawn` join ever did.

```rust
let handle = tokio::spawn(async {
    panic!("task invariant broken");
});
match handle.await {
    Ok(()) => println!("ok"),
    Err(err) => {
        println!("is_panic: {}", err.is_panic());
        println!("Display: {err}");
    }
}
println!("main is still running");
```

Three of three runs printed `is_panic: true` and, in this run, a `Display` reading `task 9 panicked with message "task invariant broken"`, the task number being incidental, followed by `main is still running`. Lesson 29's `thread::spawn().join()` also returns a `Result` on panic, but as a bare `Box<dyn Any + Send>` needing a downcast; `JoinError` already exposes `is_panic` and a way to recover the payload directly, and either way one task's panic never reaches another task or the runtime. Calling `handle.abort()` asks the runtime to cancel the task without waiting, confirmed here only as far as the handle coming back cancelled rather than panicked; what a cancelled future's own drop does is lesson 42's subject.

## Practice

1. ▢ Predict the order of these three lines, then run it.

   ```rust
   let handle = tokio::spawn(async { println!("A"); });
   println!("B");
   handle.await.unwrap();
   println!("C");
   ```

<details markdown="1"><summary>Check</summary>

`B` prints first, since `spawn` never polls synchronously; `A` prints next, once the runtime gets a chance to run the task; `C` prints last, once the handle confirms the task is done.

</details>

2. ▢ Predict which of sequential awaits, `tokio::join!`, and `tokio::spawn` could ever print two different thread ids, then run all three several times to check.

<details markdown="1"><summary>Hint</summary>

Ask how many tasks the runtime has to place, not how many futures the code mentions.

</details>

<details markdown="1"><summary>Check</summary>

Only the spawn version can: sequential awaits and `join!` both run inside the one task doing the awaiting, while spawn creates two independent tasks the scheduler may place on separate worker threads.

</details>

3. ▢ Predict whether this compiles, and if not, what the diagnostic blames, then try it.

   ```rust
   tokio::spawn(async {
       let cell = std::rc::Rc::new(1);
       sleep(Duration::from_millis(1)).await;
       println!("{cell}");
   });
   ```

<details markdown="1"><summary>Hint</summary>

Check what is still alive at the point of the `.await`, not what the value is later used for.

</details>

<details markdown="1"><summary>Check</summary>

It fails with `error: future cannot be sent between threads safely`, blaming `cell` for being alive across the `.await`, the same shape as this lesson's `touch` example: moving the `let cell = ...` line to after the `.await` would fix it.

</details>

4. ▢ Predict whether a trait's `async fn` method compiles, whether calling it directly compiles, and whether spawning it through a generic function compiles, then check each.

<details markdown="1"><summary>Hint</summary>

Ask whether the trait's signature promises anything about the thread the returned future may run on.

</details>

<details markdown="1"><summary>Check</summary>

The trait and a direct call both compile, since the concrete future type is known at that call site. Spawning it through a generic function fails: bounding the type parameter with `Send` says nothing about the opaque future its trait method returns, so only rewriting the trait to return `impl Future<...> + Send` fixes it.

</details>

5. ▢ Predict what `handle.await` produces when the spawned task panics, and whether the line after it still runs, then run it.

<details markdown="1"><summary>Check</summary>

`handle.await` produces `Err(JoinError)`, whose `is_panic` is true, and the following line still runs: one task's panic never stops the caller or any other task.

</details>

## Real-world reps

- [ ] Give your summariser one task per input source with `tokio::spawn`, collect each partial summary by awaiting its handle as lesson 30's scoped threads did, make whatever the tasks share satisfy `Send + 'static`, and write one line naming what you had to move or wrap in an `Arc` that stage 5's version never needed.
- [ ] Take this lesson's `Rc` example, replace `Rc<String>` with `Arc<String>` instead of confining the value before the await, run it, and write one line on why this is choosing the right type rather than reaching for a workaround.
- [ ] Tomorrow: pick one `tokio::spawn` call you own, and check by hand whether its future holds anything not `Send` across an await, before the compiler tells you.

## Going further

- [tokio::task::JoinHandle](https://docs.rs/tokio/1.53.1/tokio/task/struct.JoinHandle.html): the type spawn returns, and what a dropped handle does to its task
- [tokio::join!](https://docs.rs/tokio/1.53.1/tokio/macro.join.html): concurrent waiting without a second task
- [Spawning](https://tokio.rs/tokio/tutorial/spawning): a tutorial chapter working through a small multi-task server
- [Announcing Rust 1.75.0](https://blog.rust-lang.org/2023/12/28/Rust-1.75.0/): the release stabilising async fn in traits
- [Async](../reference/async.md): the stage 6 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
