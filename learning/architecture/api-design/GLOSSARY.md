---
title: Glossary
description: "Canonical terms for API design"
type: glossary
---

# API Design Glossary

Canonical terms for designing and evolving an interface others depend on.

## Terms

**Contract**:
Every behavior of an API a client can rely on, whether deliberately documented or merely observed and depended on in practice (see Hyrum's Law).
_Avoid_: interface (too broad; a contract is specifically what's relied on, not the shape of the API alone)

**Hyrum's Law**:
The principle that with enough users of an API, every observable behavior, documented or not, will end up depended on by somebody.
_Avoid_: none in particular, but do not use as an excuse to skip documenting a deliberate contract
