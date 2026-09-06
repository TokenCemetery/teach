---
title: Resources
description: "Trusted sources for API design"
type: resources
---

# API Design Resources

## Knowledge

- [RFC 9110: "HTTP Semantics", IETF](https://www.rfc-editor.org/rfc/rfc9110)
  The authoritative specification of HTTP methods, status codes, and what each actually promises a client. Use for: settling exactly what an HTTP verb or status code means, rather than relying on convention or folklore.
- [RFC 9457: "Problem Details for HTTP APIs", IETF](https://www.rfc-editor.org/rfc/rfc9457)
  A standard, machine-readable JSON format for reporting an HTTP API error, so a client can handle errors structurally instead of parsing prose. Use for: designing an error model that is actually part of the contract, not an afterthought.
- [Docs: "Language Guide (proto3)", Protocol Buffers](https://protobuf.dev/programming-guides/proto3/)
  Official guide including the specific field-numbering and type rules that determine whether a Protobuf message change is backward- or forward-compatible. Use for: evolving a gRPC contract without breaking existing clients.
- [Site: "API Improvement Proposals", Google](https://google.aip.dev/)
  Google's own practical design guide for REST and gRPC APIs: resource naming, standard methods, versioning, pagination, and more, each with its rationale. Use for: a concrete, opinionated reference when designing a contract from scratch.
- [Docs: "API versioning", Stripe](https://docs.stripe.com/api/versioning)
  A real, widely-studied production API's versioning and deprecation strategy: how it ships breaking changes without breaking every existing integration at once. Use for: a worked example of an evolution strategy, not just the theory of one.
- [Draft: "RateLimit header fields for HTTP", IETF](https://www.ietf.org/archive/id/draft-ietf-httpapi-ratelimit-headers-08.html)
  A standardization effort for communicating rate-limit state to a client via response headers. Use for: treating rate limiting as a visible, documented part of the contract rather than an undocumented 429 a client discovers by accident.

## Gaps

- No source yet specifically on authentication and authorization scheme design (API keys vs. OAuth2 vs. mTLS) as a contract-design decision, as opposed to a security-implementation detail; worth closing once lesson design reaches that success criterion.
