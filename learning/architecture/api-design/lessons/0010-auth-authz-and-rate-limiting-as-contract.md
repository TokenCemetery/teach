---
title: 10. Auth, Authz, and Rate Limiting as Contract
description: Why scopes, not just tokens, and visible rate-limit state, not just a 429, are what make access control and quotas part of the deliberate contract
type: lesson
---

# Lesson 10. Auth, Authz, and Rate Limiting as Contract

**Mission link:** This is the final lesson of the arc. Every prior lesson treated the contract as endpoints, errors, and evolution; this lesson closes the mission's third success criterion by extending the same discipline to authentication, authorization, and rate limiting, treated as what a client depends on rather than a security afterthought bolted on separately.
**Primary source:** [RFC 6749: "The OAuth 2.0 Authorization Framework", IETF](https://www.rfc-editor.org/rfc/rfc6749)
**Prerequisites:** [Lesson 9](0009-versioning-and-migration-strategy.md), [Contract](../GLOSSARY.md)

## Warm-up

1. ▢ What does giving an API contract a specific version name actually commit an API provider to?

<details markdown="1"><summary>Check</summary>

Keeping that exact version's behavior unchanged going forward, even as the API's overall design continues to evolve in newer versions. It's a frozen snapshot of the contract, not just a label.

</details>

2. ▢ Why is a migration guide that only says "this changed, update your code" insufficient?

<details markdown="1"><summary>Check</summary>

It pushes the entire cost of understanding and translating between old and new behavior onto every integrating team independently, rather than the API provider doing that translation work once, ideally with a documented mapping and a compatibility layer.

</details>

## Know this

### Authentication answers "who," authorization answers "what," and a token's scope is where authz becomes contract

Lesson 2 already distinguished `401` (no valid authentication) from `403` (authenticated, but not permitted). OAuth 2.0's **scope** mechanism is where that distinction becomes a designed, documented part of the contract rather than an opaque yes/no: a token is issued with a specific scope (`orders:read`, `orders:write`), and a client can rely on exactly what that scope grants, no more and no less, the same way it relies on a resource's URL or a field's presence. An API that hands out all-or-nothing tokens with no scope granularity has quietly decided that authorization isn't part of its contract, an accidental-contract risk in the opposite direction from lesson 1: clients build workarounds (requesting broader access than they need, since nothing narrower is offered) that become their own hard-to-change dependency.

### Choosing an auth scheme is a contract decision, not just a security implementation detail

API keys, OAuth 2.0 (with its several grant types depending on whether a human resource owner is involved), and mutual TLS each make different promises about what a client has to do to authenticate and what the API can verify about who's calling. This choice shapes the contract as much as resource modeling does: an API key is simple but coarse-grained (usually one key, one set of permissions, hard to scope narrowly); OAuth's authorization code grant supports fine-grained, user-consented scopes but requires a real authorization flow; client credentials grant fits machine-to-machine access without a human resource owner. Picking one isn't a detail to leave to whoever implements the auth middleware; it determines what a client integration actually has to build.

### Rate limiting without visible state is an undocumented, accidental contract

A client hitting `429 Too Many Requests` with no further information has to guess at the actual limit, how long to wait, and how close it was to the limit before the failure, exactly the kind of accidental, undocumented behavior lesson 1 warns clients will build fragile logic around anyway (guessing at a safe request rate through trial and error). The IETF's RateLimit header fields draft (revision 11 as of this writing, not yet an RFC) standardizes communicating this state explicitly in every response, not just a failing one, through two Structured Fields: `RateLimit-Policy` for the stable quota (a quota amount and window that shouldn't change response to response) and `RateLimit` for the caller's live standing against it (how much quota remains, and the window that remaining amount applies to), so a client can make an informed decision (slow down proactively) instead of discovering the limit only by tripping over it. A quota failure isn't a bare `429` either: the draft registers RFC 9457 Problem Details types that distinguish "you asked for too much" from "the server has less capacity right now," a difference a status code alone can't express.

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    C->>S: request 1
    S-->>C: 200 OK, RateLimit: "default";r=5;t=30
    C->>S: request 2
    S-->>C: 200 OK, RateLimit: "default";r=4;t=30
    Note over C,S: state visible on every response, not just a failing one
    C->>S: request N (limit reached)
    S-->>C: 429 Too Many Requests, RateLimit: "default";r=0;t=30
```

### The mission's closing point: none of these are bolted on after design, they're part of it

Treating auth, authz, and rate limiting as contract means deciding, at the same time resources (lesson 4), errors (lessons 2-3), and evolution strategy (lessons 8-9) are decided: what scopes exist and what each one actually grants; which auth scheme fits the actual clients (human-facing versus machine-to-machine); and what rate-limit information a client can rely on seeing before it fails. An API where these are added later, whatever the security team's default middleware happens to produce, is exactly the kind of contract that grew accidentally instead of being designed, the mission's opening observation applied to security and quotas instead of resources and errors.

## Practice

1. ▢ How does OAuth 2.0 scope turn authorization from an opaque yes/no into a documented, checkable part of the contract?

<details markdown="1"><summary>Check</summary>

A token is issued with a specific, named scope (like `orders:read`), and a client can rely on exactly what that scope grants access to, rather than authorization being an internal, undocumented decision the API makes. This makes "what can this token do" a checkable, designed part of the contract rather than a black box.

</details>

2. ▢ Why does handing out only broad, all-or-nothing tokens (no scope granularity) create the same kind of risk lesson 1 describes for undocumented behavior?

<details markdown="1"><summary>Hint</summary>

Consider what a client actually does when the access it needs isn't offered at a narrower granularity.

</details>

<details markdown="1"><summary>Check</summary>

Without a narrower scope available, clients request and depend on broader access than they actually need, since nothing more precise exists. That over-broad access becomes its own hard-to-change dependency, the authorization equivalent of Hyrum's Law: clients build on whatever access shape is actually available, not the ideal, minimal one.

</details>

3. ▢ Contrast an API key and OAuth's authorization code grant as auth scheme choices. What does each assume about the client?

<details markdown="1"><summary>Check</summary>

An API key assumes a simple, usually coarse-grained trust model, often one key mapping to one broad set of permissions, with no real distinction for a human resource owner's consent. OAuth's authorization code grant assumes a human resource owner is involved and needs to consent to specific scopes through a real authorization flow, supporting fine-grained, user-approved permissions at the cost of more implementation complexity for the client.

</details>

4. ▢ Why is a bare `429` with no further headers or information an accidental contract, in the same sense lesson 1 uses the term?

<details markdown="1"><summary>Check</summary>

Without visible rate-limit state (remaining requests, the limit, the reset time), a client has no documented information to act on and instead learns the actual limit through trial and error, then builds retry or backoff logic around that discovered, undocumented behavior. That discovered behavior becomes something the client depends on exactly the way any other unpromised observable behavior does, per Hyrum's Law.

</details>

5. ▢ Which claim correctly describes treating auth, authz, and rate limiting as contract?

    - a) These are security and infrastructure concerns that should be handled entirely separately from API design
    - b) Scopes, the choice of auth scheme, and visible rate-limit state are all deliberate contract decisions that should be designed alongside resources, errors, and evolution strategy, not added afterward by default middleware
    - c) An API key and OAuth 2.0 are functionally interchangeable, so the choice between them doesn't affect the contract
    - d) Rate limiting only needs to be visible in the response that actually triggers a 429

<details markdown="1"><summary>Check</summary>

**b)** That's the mission's closing point, applying the same contract discipline from every prior lesson to access control and quotas. (a) is false: exactly the "bolted on separately" anti-pattern the mission's success criterion names. (c) is false: they assume different client capabilities and grant different granularity, a real design difference. (d) is false: the IETF draft's whole point is surfacing rate-limit state on every response, not just the failing one, so a client can act proactively.

</details>

## Real-world reps

- [ ] Find a real API's authentication scheme (one you use or maintain). Check whether it issues scoped tokens or all-or-nothing access, and whether the available scopes match what clients actually need or force over-broad requests.
- [ ] For the same API, check whether its responses include rate-limit state (remaining requests, reset time) on successful requests, or only reveal the limit once a client actually gets a `429`.
- [ ] Tomorrow: read the primary source's sections on grant types and scope in full, and note which grant type would fit a machine-to-machine integration (no human resource owner) versus a user-facing one.

## Going further

- [RFC 6749: "The OAuth 2.0 Authorization Framework", IETF](https://www.rfc-editor.org/rfc/rfc6749)
- [Draft: "RateLimit header fields for HTTP", IETF](https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/)
- [Auth and Rate Limiting](../reference/auth-and-rate-limiting.md): the `RateLimit-Policy`/`RateLimit` parameters in full, what a client may and may not conclude from them, and the three registered problem types
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
