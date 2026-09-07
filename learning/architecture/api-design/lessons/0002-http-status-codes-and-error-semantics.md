---
title: 2. HTTP Status Codes and Error Semantics
description: What a status code actually promises a client about safety, idempotency, and what to do next, beyond the vague 2xx/4xx/5xx grouping
type: lesson
---

# Lesson 2. HTTP Status Codes and Error Semantics

**Mission link:** Stage 2 opens the error model. Lesson 1 established that an error shape is as much a contract as a success shape; this lesson is what a status code specifically promises, the foundation lesson 3's structured error format builds on.
**Primary source:** [RFC 9110: "HTTP Semantics", IETF](https://www.rfc-editor.org/rfc/rfc9110)
**Prerequisites:** [Lesson 1](0001-the-contract.md), [Contract](../GLOSSARY.md)

## Warm-up

1. ▢ Why is the contract a client actually depends on bigger than what an API's documentation says?

<details markdown="1"><summary>Check</summary>

Because clients build logic around any observable behavior, documented or not (Hyrum's Law), so anything reliably observable functions as part of the actual contract regardless of whether it was ever promised.

</details>

2. ▢ Why is a response's error shape as much a contract as its success shape?

<details markdown="1"><summary>Check</summary>

A client that needs to react differently to different failure reasons (invalid input, transient failure, missing resource) needs that distinction to be a reliable, documented, machine-readable part of the response, not something inferred from a status code alone or parsed from human-readable text.

</details>

## Know this

### A status code's class is a coarse promise, not the whole one

The `1xx`/`2xx`/`3xx`/`4xx`/`5xx` classes each carry a general meaning (informational, success, redirection, client error, server error), but RFC 9110 defines individual codes within each class with much more specific promises. Treating all `4xx` as "client did something wrong, don't retry" or all `5xx` as "server broke, maybe retry" throws away exactly the distinctions a client needs to act correctly.

### The retry-safety distinction most engineers get wrong

`429 Too Many Requests` and `503 Service Unavailable` both mean "not right now," and both are meant to be retried, ideally after the duration in a `Retry-After` header if present. `400 Bad Request` means the request itself is malformed; retrying identically will fail identically, no amount of waiting fixes it. Conflating these (treating every non-2xx as either "always retry" or "never retry") produces either a client that hammers a server that told it to back off, or one that gives up on a request that would have succeeded on a second attempt.

### 404 vs. 403 vs. 401 are three different promises, not shades of "no"

`401 Unauthorized` means the request lacks valid authentication entirely; `403 Forbidden` means authentication was fine but the authenticated party isn't allowed to do this; `404 Not Found` means, per RFC 9110, either the resource genuinely doesn't exist, or the server is choosing not to reveal its existence, which is itself a deliberate design decision (some APIs return `404` instead of `403` specifically to avoid confirming a resource's existence to an unauthorized caller). Collapsing these to one generic "access denied" error throws away information a client, or a developer debugging against the API, needs.

### Idempotency is a promise a status code alone doesn't fully carry

A method being idempotent (`GET`, `PUT`, `DELETE`) means repeating the same request has the same effect as making it once; this is a property of the *method*, defined by RFC 9110, not of any particular status code returned. A `201 Created` in response to a `POST` signals a new resource was created, and `POST` is *not* idempotent by default, meaning retrying a timed-out `POST` risks creating the resource twice unless the API separately provides an idempotency mechanism (an idempotency key, a client-supplied resource ID via `PUT` instead). Confusing "this status code looked successful" with "this request is safe to retry" is a common, concrete source of duplicate-resource bugs.

## Practice

1. ▢ A client receives a `503` and, right after, a `400` for a similar-looking request. Should it retry either, both, or neither, and why?

<details markdown="1"><summary>Check</summary>

Retry the `503` (ideally honoring a `Retry-After` header if present), since it signals a transient, likely temporary problem on the server's side. Do not retry the `400` identically, since it signals the request itself is malformed; an identical retry will fail identically until the request is actually fixed.

</details>

2. ▢ Explain the difference in what `401` and `403` each promise a client, and why collapsing both into "access denied" loses information.

<details markdown="1"><summary>Hint</summary>

Consider what a client needs to do differently to fix each situation.

</details>

<details markdown="1"><summary>Check</summary>

`401` means the request lacks valid authentication at all, so the fix is to authenticate (log in, supply a valid token). `403` means authentication succeeded but the authenticated party lacks permission for this specific action, so the fix is different (request access, use a different account), not re-authenticating. A client (or a developer) that sees only "access denied" can't tell which fix applies.

</details>

3. ▢ Why is "is idempotent" a property of the request method, not of the status code returned?

<details markdown="1"><summary>Check</summary>

Idempotency describes whether repeating the identical request has the same effect as making it once, which is defined by RFC 9110 per HTTP method (`GET`, `PUT`, `DELETE` are idempotent by definition; `POST` is not). The status code returned tells you the outcome of one specific attempt; it doesn't change what repeating that same request would do, which is a property of the method itself.

</details>

4. ▢ A client's `POST` request to create an order times out with no response received. The client, assuming failure, retries the identical `POST`. What's the risk, and what's one way an API could make this retry safe?

<details markdown="1"><summary>Check</summary>

The risk is a duplicate order: since `POST` isn't idempotent, the original request may have actually succeeded server-side even though the client never received the response, and the retry creates a second order. An API can make this safe by supporting an idempotency key the client supplies (so the server can recognize and deduplicate a repeated request with the same key) or by using `PUT` with a client-supplied resource identifier instead of `POST`, since `PUT` is idempotent by definition.

</details>

5. ▢ Which claim correctly describes what a status code promises?

    - a) All `4xx` codes mean the same thing: don't retry, the client is at fault
    - b) A specific status code (like `429` vs. `400`) carries a distinct, spec-defined meaning about what happened and what the client should do next, which the broader `2xx`/`4xx`/`5xx` class alone doesn't convey
    - c) A `201 Created` response guarantees the request that produced it is safe to retry
    - d) `404` always means the resource genuinely doesn't exist

<details markdown="1"><summary>Check</summary>

**b)** That's the actual, specific promise a status code carries, well beyond its coarse class. (a) is false: `429` and `400` are both `4xx` but call for opposite retry behavior. (c) is false: `201` reports the outcome of one attempt; it says nothing about whether the underlying method (often `POST`) is safe to repeat. (d) is false: RFC 9110 explicitly allows `404` to be used deliberately to avoid revealing a resource's existence to an unauthorized caller, not only for genuine absence.

</details>

## Real-world reps

- [ ] Find a real API's error-handling code in a codebase you know of (a client library, a service's retry logic). Check whether it distinguishes retryable status codes (`429`, `503`) from non-retryable ones (`400`), or treats all non-2xx responses the same way.
- [ ] For that same codebase, check whether any `POST` endpoint that creates a resource has an idempotency mechanism, and if not, what would actually happen on a client-side retry after a timeout.
- [ ] Tomorrow: read RFC 9110's definitions of `401`, `403`, and `404` in full, and note the specific language around when `404` is permitted to be used instead of `403` or `401`.

## Going further

- [RFC 9110: "HTTP Semantics", IETF](https://www.rfc-editor.org/rfc/rfc9110)
- [RFC 9457: "Problem Details for HTTP APIs", IETF](https://www.rfc-editor.org/rfc/rfc9457)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
