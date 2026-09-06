---
title: Glossary
description: "Canonical terms for distributed systems"
type: glossary
---

# Distributed Systems Glossary

Canonical terms for reasoning about partial failure, consistency, and consensus once the process boundary is crossed.

## Terms

**Partial failure**:
The failure mode unique to distributed systems: a request produces no response, and the caller cannot tell whether it was lost in transit, its reply was lost, or the other side is merely slow.
_Avoid_: network error (too specific; partial failure includes cases with no error at all, just silence)

**Timeout**:
A caller's chosen limit on how long to wait for a response before treating the other side as failed. A guess made under permanent uncertainty, not a fact, since a network has no upper bound on message delay.
_Avoid_: deadline (use only when quoting a source or API that uses that specific term)
