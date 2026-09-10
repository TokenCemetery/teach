---
title: Resources
description: "Trusted sources for API design"
type: resources
---

# API Design Resources

## Knowledge

- [RFC 9110: "HTTP Semantics", IETF](https://www.rfc-editor.org/rfc/rfc9110)
  The authoritative specification of HTTP methods, status codes, and what each actually promises a client. Use for: settling exactly what an HTTP verb or status code means, rather than relying on convention or folklore.
- [RFC 6585: "Additional HTTP Status Codes", IETF](https://www.rfc-editor.org/rfc/rfc6585)
  Defines `429 Too Many Requests`, which RFC 9110 does not, along with the rule that a `429` response must not be stored by a cache. Use for: settling what a rate-limit response actually promises, and citing the right document when RFC 9110 turns out not to contain the code.
- [Site: "Hyrum's Law", hyrumslaw.com](https://www.hyrumslaw.com/)
  States the principle that with enough users of an API, every observable behavior, documented or not, will end up depended on by somebody. Use for: understanding why the contract a client actually relies on is bigger than what you documented, and why "harmless, undocumented" changes still break clients.
- [RFC 9457: "Problem Details for HTTP APIs", IETF](https://www.rfc-editor.org/rfc/rfc9457)
  A standard, machine-readable JSON format for reporting an HTTP API error, so a client can handle errors structurally instead of parsing prose. Use for: designing an error model that is actually part of the contract, not an afterthought.
- [Docs: "Core concepts, architecture and lifecycle", gRPC](https://grpc.io/docs/what-is-grpc/core-concepts/)
  Official overview of gRPC's service definitions and its four RPC kinds (unary, server streaming, client streaming, bidirectional streaming), with the specific ordering and completion guarantees each provides. Use for: choosing the right RPC kind for a given use case, not defaulting to unary out of familiarity.
- [Docs: "Status Codes", gRPC](https://grpc.io/docs/guides/status-codes/)
  Official reference for gRPC's status codes, what each means, and which are reserved for library-generated errors versus application use. Use for: designing a gRPC error model with the same precision RFC 9110 brings to HTTP status codes.
- [Proto: `google.rpc.Code`, googleapis](https://github.com/googleapis/googleapis/blob/master/google/rpc/code.proto)
  The canonical status-code enumeration behind gRPC, whose comments carry the official HTTP status each code maps to. Use for: mapping a gRPC code to an HTTP one without inventing the correspondence, and for seeing where the mapping is lossy because several codes share one status.
- [Docs: "Language Guide (proto3)", Protocol Buffers](https://protobuf.dev/programming-guides/proto3/)
  Official guide including the specific field-numbering and type rules that determine whether a Protobuf message change is backward- or forward-compatible. Use for: evolving a gRPC contract without breaking existing clients.
- [Docs: "ProtoJSON Format", Protocol Buffers](https://protobuf.dev/programming-guides/json/)
  The JSON representation of a Protobuf message, and the schema-evolution guarantees it does **not** share with the binary wire format: names are carried in the payload, unknown fields are unsupported, and removing a field is a parse error. Use for: deciding whether a rename or a deletion is safe, once a service exposes JSON as well as gRPC.
- [Site: "API Improvement Proposals", Google](https://google.aip.dev/)
  Google's own practical design guide for REST and gRPC APIs: resource naming, standard methods, versioning, pagination, and more, each with its rationale. Use for: a concrete, opinionated reference when designing a contract from scratch.
- [Docs: "API versioning", Stripe](https://docs.stripe.com/api/versioning)
  A real, widely-studied production API's versioning and deprecation strategy: how it ships breaking changes without breaking every existing integration at once. Use for: a worked example of an evolution strategy, not just the theory of one.
- [Docs: "API upgrades", Stripe](https://docs.stripe.com/upgrades)
  The companion to the versioning page: the named-release scheme, how a version is set and overridden, and Stripe's own enumerated list of what it counts as a backward-compatible change. Use for: a production API's written definition of "not breaking", including the two entries most teams would not think to declare, property order and the format of an opaque ID.
- [RFC 9745: "The Deprecation HTTP Response Header Field", IETF](https://www.rfc-editor.org/rfc/rfc9745)
  Standardizes the `Deprecation` response header as a date, plus the `deprecation` link relation for pointing at a policy. Use for: making a deprecation visible to a client's tooling rather than only to a human reading a changelog, and for the correct syntax, which is not the `Deprecation: true` of the earlier draft.
- [RFC 8594: "The Sunset HTTP Header Field", IETF](https://www.rfc-editor.org/rfc/rfc8594)
  Defines the `Sunset` header, which says when a resource is expected to stop responding. Use for: pairing a deprecation date with the removal date it implies, remembering that the two headers deliberately use different date formats.
- [Draft: "RateLimit header fields for HTTP", IETF](https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/)
  A standardization effort for communicating rate-limit state to a client via response headers, still a draft rather than an RFC. Use for: treating rate limiting as a visible, documented part of the contract rather than an undocumented 429 a client discovers by accident. Linked to the tracker rather than to a revision on purpose, because the design has already changed once: the three separate headers of the early revisions became the `RateLimit-Policy` and `RateLimit` structured fields, plus registered Problem Details types.
- [RFC 6749: "The OAuth 2.0 Authorization Framework", IETF](https://www.rfc-editor.org/rfc/rfc6749)
  The authoritative spec for OAuth 2.0's roles, grant types, and scopes, the mechanism by which an API expresses exactly what a token grants. Use for: treating authorization scope as a deliberate, documented part of the contract rather than an implementation detail bolted on after the fact.
- [RFC 6750: "The OAuth 2.0 Authorization Framework: Bearer Token Usage", IETF](https://www.rfc-editor.org/rfc/rfc6750)
  Defines how a bearer token is presented and, more usefully for design, the `error` codes a resource server returns in `WWW-Authenticate`: `invalid_request`, `invalid_token`, `insufficient_scope`, each with the status code it belongs to. Use for: making a refusal machine-readable, and for the rule that a request with no authentication at all gets a challenge with no error code.
- [RFC 9700: "Best Current Practice for OAuth 2.0 Security", IETF](https://www.rfc-editor.org/rfc/rfc9700)
  BCP 240, updating RFC 6749, 6750 and 6819. Retires two of OAuth's original four grant types: the resource owner password credentials grant must not be used, and clients should not use the implicit grant. Use for: checking that the grants an API offers are ones still recommended, rather than the four RFC 6749 listed in 2012.
- [Draft: "The Idempotency-Key HTTP Header Field", IETF HTTPAPI Working Group](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)
  A standardization effort (still a draft, not yet an RFC) for the header that makes a non-idempotent method like `POST` safe to retry. Use for: the idempotency-fingerprint mechanism, the exact three-way enforcement outcome (first time, retry-after-completion, concurrent-in-flight), and the specific `400`/`422` error cases.
- [RFC 9111: "HTTP Caching", IETF](https://www.rfc-editor.org/rfc/rfc9111)
  The authoritative specification for `Cache-Control` and cache behavior. Use for: the precise, commonly-confused difference between `no-cache` (permits storage, requires revalidation before reuse) and `no-store` (forbids storage entirely), and what `must-revalidate` adds once a response is stale.
- [AIP-151: "Long-running operations", Google](https://google.aip.dev/151)
  Google's design guidance for the operation-resource pattern. Use for: the exact shape of an operation resource (`name`, `done`, `metadata`, `response`/`error`), the distinction between a failure to start and a failure during execution, and the ~30-day expiration rule of thumb.
- [Docs: "Receive Stripe events in your webhook endpoint", Stripe](https://docs.stripe.com/webhooks)
  A real, production webhook implementation's documented contract. Use for: the `Stripe-Signature` header's timestamp-based replay protection (and the common mistake of setting its tolerance to 0), the multi-day exponential-backoff retry policy, and the explicit statement that event delivery order is not guaranteed.
