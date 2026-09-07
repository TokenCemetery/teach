---
title: Resources
description: "Trusted sources for API design"
type: resources
---

# API Design Resources

## Knowledge

- [RFC 9110: "HTTP Semantics", IETF](https://www.rfc-editor.org/rfc/rfc9110)
  The authoritative specification of HTTP methods, status codes, and what each actually promises a client. Use for: settling exactly what an HTTP verb or status code means, rather than relying on convention or folklore.
- [Site: "Hyrum's Law", hyrumslaw.com](https://www.hyrumslaw.com/)
  States the principle that with enough users of an API, every observable behavior, documented or not, will end up depended on by somebody. Use for: understanding why the contract a client actually relies on is bigger than what you documented, and why "harmless, undocumented" changes still break clients.
- [RFC 9457: "Problem Details for HTTP APIs", IETF](https://www.rfc-editor.org/rfc/rfc9457)
  A standard, machine-readable JSON format for reporting an HTTP API error, so a client can handle errors structurally instead of parsing prose. Use for: designing an error model that is actually part of the contract, not an afterthought.
- [Docs: "Core concepts, architecture and lifecycle", gRPC](https://grpc.io/docs/what-is-grpc/core-concepts/)
  Official overview of gRPC's service definitions and its four RPC kinds (unary, server streaming, client streaming, bidirectional streaming), with the specific ordering and completion guarantees each provides. Use for: choosing the right RPC kind for a given use case, not defaulting to unary out of familiarity.
- [Docs: "Status Codes", gRPC](https://grpc.io/docs/guides/status-codes/)
  Official reference for gRPC's status codes, what each means, and which are reserved for library-generated errors versus application use. Use for: designing a gRPC error model with the same precision RFC 9110 brings to HTTP status codes.
- [Docs: "Language Guide (proto3)", Protocol Buffers](https://protobuf.dev/programming-guides/proto3/)
  Official guide including the specific field-numbering and type rules that determine whether a Protobuf message change is backward- or forward-compatible. Use for: evolving a gRPC contract without breaking existing clients.
- [Site: "API Improvement Proposals", Google](https://google.aip.dev/)
  Google's own practical design guide for REST and gRPC APIs: resource naming, standard methods, versioning, pagination, and more, each with its rationale. Use for: a concrete, opinionated reference when designing a contract from scratch.
- [Docs: "API versioning", Stripe](https://docs.stripe.com/api/versioning)
  A real, widely-studied production API's versioning and deprecation strategy: how it ships breaking changes without breaking every existing integration at once. Use for: a worked example of an evolution strategy, not just the theory of one.
- [Draft: "RateLimit header fields for HTTP", IETF](https://www.ietf.org/archive/id/draft-ietf-httpapi-ratelimit-headers-08.html)
  A standardization effort for communicating rate-limit state to a client via response headers. Use for: treating rate limiting as a visible, documented part of the contract rather than an undocumented 429 a client discovers by accident.
- [RFC 6749: "The OAuth 2.0 Authorization Framework", IETF](https://www.rfc-editor.org/rfc/rfc6749)
  The authoritative spec for OAuth 2.0's roles, grant types, and scopes, the mechanism by which an API expresses exactly what a token grants. Use for: treating authorization scope as a deliberate, documented part of the contract rather than an implementation detail bolted on after the fact.
