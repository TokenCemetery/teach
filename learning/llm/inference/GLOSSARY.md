---
title: Glossary
description: "Canonical terms for inference"
type: glossary
---

# Inference Glossary

Canonical terms for serving a trained model: what a server holds in memory, and the levers it has over latency and throughput.

## Terms

**KV cache**:
The stored key and value vectors for every already-generated token, at every layer, kept so a server never has to recompute them for later tokens. Its size grows linearly with sequence length and is often the memory bottleneck in serving, not the model's own weights.
_Avoid_: attention cache, key-value store
