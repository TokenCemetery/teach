---
title: Glossary
description: "Canonical terms for LLM agents"
type: glossary
---

# LLM Agents Glossary

Canonical terms for building agents: what the loop is made of, and what to call each part in a field that routinely uses four words for one thing.

## Terms

**Agent**:
A system that runs a language model in a loop with tools, letting the model decide which tool to call, when, and when to stop, rather than following a path the developer fixed in advance.
_Avoid_: assistant, bot, copilot (product words that say nothing about whether the control flow is fixed or model-decided)

**Agent loop**:
The cycle a running agent repeats: send the transcript to the model, execute whatever tool call comes back, append the result to the transcript, repeat until a stopping condition fires.
_Avoid_: chain, pipeline (both name a fixed sequence, which is exactly what an agent loop is not)

**Harness**:
The code around the model that holds the transcript, executes tool calls, enforces limits, and decides when the loop ends. The model chooses; the harness acts.
_Avoid_: runtime, framework (a framework is one possible harness, not the concept)

**Tool**:
A capability offered to the model as a name, a description and a parameter schema, which the model can ask for and the harness executes on its behalf.
_Avoid_: function call (that names the message the model emits, not the capability), plugin, skill

**Trajectory**:
The full ordered record of one agent run: every model turn, tool call, tool result and stopping decision. It is what gets read when diagnosing a failure, rather than the final answer alone.
_Avoid_: transcript (the message list the model actually sees, which omits the harness's own decisions), history, log

**Workflow**:
A system where a developer fixed the sequence of model calls and tool calls in advance. It may contain branches and loops, but the model does not choose the path.
_Avoid_: agent (the distinction between the two is the point of stage 1), chain
