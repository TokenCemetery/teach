---
title: Auth and Rate Limiting
description: "Scopes and grant types as contract, the error codes a resource server owes a client, and the RateLimit fields that make a quota visible"
type: reference
---

# Auth and Rate Limiting as Contract

Stage 6 compressed for lookup. [Lesson 10](../lessons/0010-auth-authz-and-rate-limiting-as-contract.md) covers why access control and quotas are part of what a client depends on; this sheet is the mechanisms, with what each one obliges you to tell a client.

## What the resource server owes a caller

Two of the three status codes come from [Error Models](error-models.md). What RFC 6750 adds is the machine-readable reason, carried in `WWW-Authenticate`.

| Situation | Status | `error` code |
|---|---|---|
| No authentication information at all | `401` | **None.** RFC 6750 says do not include an error code, just the challenge |
| Token expired, revoked, malformed, or otherwise invalid | `401` | `invalid_token`. The client may get a new token and retry |
| Token valid, privileges too low | `403` | `insufficient_scope`, and the response may name the `scope` needed |
| Malformed request, or more than one way of presenting a token | `400` | `invalid_request` |

```http
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer realm="example", error="insufficient_scope", scope="orders:write"
```

Naming the required scope in the challenge is the difference between a client that can fix the problem and one that can only file a support ticket.

## Scopes

From RFC 6749 section 3.3, and every line of it is contract.

| Rule | Consequence for a client |
|---|---|
| Space-delimited, case-sensitive strings defined by the authorization server | `orders:read` and `Orders:Read` are different scopes |
| Order does not matter, and each string adds an access range | A scope set is a set, not a sequence |
| The server **may** ignore the requested scope in part or in full | Asking for a scope is not receiving it |
| If the granted scope differs from the request, the server **must** return a `scope` parameter | So a client can always discover what it actually got, and should read it rather than assume |
| If the client omits `scope`, the server must apply a documented default or fail with an invalid-scope error | Silence is not "everything" |
| The server **should** document its scope requirements and its default | This is the part teams skip, and it is the part clients need |

An API with one all-or-nothing token has not avoided the decision; it has decided that authorization is not part of its contract. Clients then request more access than they need, because nothing narrower exists, and that over-broad grant becomes its own dependency nobody can unwind later.

## Grant types, and which are still recommended

RFC 6749 defines four. RFC 9700, the OAuth 2.0 security best current practice published in January 2025, retires two of them.

| Grant | Fits | Status |
|---|---|---|
| Authorization code | A human resource owner consenting to scoped access | Recommended, and the one to use instead of implicit |
| Client credentials | Machine to machine, no human in the loop | Fine |
| Implicit | Browser apps, historically | Clients **should not** use it. Access tokens in the authorization response leak and can be replayed, and there is no standard way to sender-constrain them |
| Resource owner password credentials | Collecting a username and password directly | **Must not** be used. It exposes the resource owner's credentials to the client, trains users to type credentials outside the authorization server, and does not work with multi-factor flows |

### Choosing a scheme is choosing what clients must build

| Scheme | What a client has to do | What it costs the contract |
|---|---|---|
| API key | Send a header | Coarse. One key, one set of permissions, and narrowing it later is a breaking change |
| OAuth 2.0 authorization code | Implement a redirect flow, store and refresh tokens | Fine-grained, user-consented scopes, at real integration cost |
| OAuth 2.0 client credentials | Exchange credentials for a token | Scoped machine access without a consent flow |
| Mutual TLS | Provision and rotate a client certificate | Strong identity, and certificate lifecycle becomes part of the integration |

## Rate limiting

The IETF work here is **still a draft**, currently revision 11 of `draft-ietf-httpapi-ratelimit-headers`, not an RFC. It is worth following anyway, because it is the only serious attempt at making a quota visible, but implement it knowing the shape can still move.

**It already has moved.** Earlier revisions defined three separate headers along the lines of a limit, a remaining count and a reset time. The current draft replaces that with two Structured Fields.

### `RateLimit-Policy`, the stable part

What the quota policy is. It should stay the same across responses, which is what distinguishes it from the field below.

```http
RateLimit-Policy: "burst";q=100;w=60,"daily";q=1000;w=86400
```

| Parameter | Required | Meaning |
|---|---|---|
| `q` | yes | The quota allocated by this policy, in quota units |
| `qu` | no | The quota unit. Defaults to `requests`, and can be something else, such as `content-bytes` |
| `w` | no | The time window |
| `pk` | no | The partition key the quota is counted against |

### `RateLimit`, the live part

Where this caller currently stands, and it may change on every request.

```http
RateLimit: "default";r=50;t=30
```

| Parameter | Required | Meaning |
|---|---|---|
| `r` | yes | Available quota under the named policy, a non-negative integer in quota units |
| `t` | no | The effective window: the time within which no more than `r` may be used |
| `pk` | no | The partition key for this request |

Both fields are Lists, so several policies can be reported at once, and a vendor-specific parameter should carry a vendor prefix. `RateLimit` must not appear in a trailer.

### What a client may and may not conclude

- **A positive `r` is not a promise.** The draft says explicitly that clients must not assume available quota guarantees the next request is served; other conditions apply.
- **The fields may vanish.** A client must not assume future responses carry the same fields, or any at all.
- **Malformed fields must be ignored**, not guessed at.
- **`Retry-After` wins.** If a response carries both `RateLimit` and `Retry-After`, `Retry-After` takes precedence over the effective window.
- **The window is measured at response time**, so a client on a slow link may do better using the `Date` header than trusting `t` literally.
- **`RateLimit-Policy` is informative** and may be ignored, which is the reverse of how most teams would expect a policy to be treated.

### Three problem types, which is where stage 6 rejoins stage 2

The draft registers RFC 9457 problem types, so a quota failure is not a bare `429`. Each defines a `violated-policies` extension member listing the policy names that were exceeded.

| Problem type | Typical status | Says |
|---|---|---|
| `#quota-exceeded` | `429` | The client went over one or more quota policies |
| `#temporary-reduced-capacity` | `503` | Not the client's fault. Capacity dropped, and the server may send a temporarily lower `RateLimit-Policy` |
| `#abnormal-usage-detected` | `429` | The server thinks the request pattern is unintentional or malicious |

The middle one is the interesting design point: it separates "you asked for too much" from "we have less to give right now", which a status code alone cannot express and which a client should react to differently.

## Before shipping access control and quotas

- Every scope that exists is documented, along with what it grants and what the default is when a client asks for none.
- A `403` says which scope would have worked.
- A `401` for a missing token carries a challenge and no error code; a `401` for a bad token carries `invalid_token`.
- The grant types offered exclude the two RFC 9700 retires.
- Quota state is visible on successful responses, not only on the one that fails.
- A quota failure carries a problem type a client can branch on, and the reason for the refusal distinguishes the client's usage from the server's capacity.
- Anything a client can observe about the limit, including whether the headers appear at all, is either documented or deliberately not promised.

## Sources

- [RFC 6749: "The OAuth 2.0 Authorization Framework", IETF](https://www.rfc-editor.org/rfc/rfc6749)
- [RFC 6750: "The OAuth 2.0 Authorization Framework: Bearer Token Usage", IETF](https://www.rfc-editor.org/rfc/rfc6750)
- [RFC 9700: "Best Current Practice for OAuth 2.0 Security", IETF](https://www.rfc-editor.org/rfc/rfc9700)
- [Draft: "RateLimit header fields for HTTP", IETF](https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/)
- [Error Models](error-models.md)
- [Resources](../RESOURCES.md)
