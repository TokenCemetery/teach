---
title: 21. What a Prompt Cannot Defend
description: Which defences belong in the prompt, and why the real ones sit in what the system lets the model do
type: lesson
---

# Lesson 21. What a Prompt Cannot Defend

**Mission link:** Design a prompt that handles untrusted input, and say which risks the prompt cannot defend against on its own. This lesson sorts the defences into the ones a prompt author owns and the ones the system has to enforce.
**Primary source:** [Docs: "Mitigate jailbreaks and prompt injections", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks)
**Prerequisites:** [Lesson 4](0004-structure-and-delimiters.md), [Lesson 20](0020-prompt-injection.md), [instruction hierarchy](../GLOSSARY.md)

## Warm-up

1. ▢ What are the two routes by which injected text reaches a prompt, and which one does a screen on the chat box miss?

<details markdown="1"><summary>Check</summary>

Direct, where the user types it, and indirect, where it sits in content the model reads on the user's behalf, such as a web page or a retrieved chunk. A screen on the chat box misses indirect injection, because that text never passes through the box.

</details>

2. ▢ In a prompt template, why must the fixed text and the filled variables stay clearly apart?

<details markdown="1"><summary>Check</summary>

The variables carry per-request text, some of it untrusted. If a value can end the structure the template built, for example by closing a tag, the data can pass as instructions. Lesson 15 covers escaping so a value cannot do that.

</details>

3. ▢ What does an instruction placed in the system prompt have going for it that the same sentence in a retrieved document lacks?

<details markdown="1"><summary>Check</summary>

Position in the instruction hierarchy. A model trained on the hierarchy gives the system prompt more weight than content from tools or retrieval, so the same words carry different authority depending on where they sit.

</details>

## Know this

### What the prompt can do

These defences are the prompt author's to build. Each lowers the chance an injection works. None of them removes it.

**Delimit untrusted input and say what it is.** Wrap each untrusted slot in tags (lesson 4) and escape the value (lesson 15). Anthropic adds a second step: make the nature and source of the content explicit, for example that it is the body of an inbound email from an unknown sender, which "helps Claude calibrate how much to trust embedded directives". Its guide also shows a structural option, encoding the content as a JSON string so that "the encoding makes it unambiguous that this is data".

**State the policy in the system prompt.** Anthropic's wording: tell the model that content returned from tools, documents or searches is untrusted data and must never override the system prompt or the user's original request. This is the instruction hierarchy written out for the model, so it reinforces what the model was trained to do.

**Keep your own instructions out of untrusted channels.** Anthropic's guidance is to deliver third-party content in tool results and send your instructions in a user turn after them, because instructions placed inside tool results "may be ignored or flagged as a potential injection".

**Lean on instruction hierarchy training, but do not own it.** Wallace et al. trained a model (GPT-3.5 in the paper) on data that demonstrates following the higher-privileged instruction, and report that it "drastically increases robustness", including for attack types not seen in training, with minimal degradation on standard capabilities. That is a property of the model you choose. You get it by choosing a model trained this way and by placing text at the right level, not by wording your prompt.

**Screen input.** Anthropic recommends a lightweight model as a harmlessness screen on user input, constrained to a simple classification with structured output, and input validation for known injection patterns. The same pattern applies to tool outputs before the main model acts on them. A screen is another model call with its own error rate, and Anthropic's page notes that a screening call can itself be declined, which you must handle as a verdict, not ignore.

### Why this is not a security boundary

Every item above reduces likelihood. The question is whether any of them guarantees the outcome, and the sources say not.

- Willison: "you can try telling it not to in your own prompt, but how confident can you be that your protection will work every time?" He is also "deeply suspicious" of guardrail products claiming to catch "95% of attacks", because "in web application security 95% is very much a failing grade".
- OWASP: "it is unclear if there are fool-proof methods of prevention for prompt injection", and it lists measures that "can mitigate the impact".
- Greshake et al., in 2023: effective mitigations were "currently lacking".
- Anthropic's own page frames its steps as strengthening guardrails and pairs them with least privilege and red-teaming, not as a replacement for them.

A prompt is a request to a probabilistic reader. A security boundary is something that holds when the reader misbehaves. So the design question changes from "how do I make the model refuse?" to "what is the worst the model can do if it obeys the attacker?"

### What the system has to enforce

```mermaid
flowchart TD
    A[Feature design] --> B{Private data in reach?}
    B -->|No| Z[Injection can mislead, not steal]
    B -->|Yes| C{Untrusted content in context?}
    C -->|No| Z
    C -->|Yes| D{A way to send data out?}
    D -->|No| Z
    D -->|Yes| E[Lethal trifecta: remove one leg]
```

**The lethal trifecta.** Willison names three capabilities that together make injection exploitable: access to your private data, exposure to untrusted content, and the ability to communicate externally in a way that could steal the data. "If your agent combines these three features, an attacker can easily trick it into accessing your private data and sending it to that attacker." His defence for users mixing tools is to avoid the combination entirely. Lesson 31 of the agents track works this through for an agent with tools; this lesson only asks you to check your own feature against the three legs. See [the agents lesson](../../agents/lessons/0031-prompt-injection-and-the-lethal-trifecta.md).

**Least privilege.** Both OWASP and Anthropic say the same thing: give the model only the access its task needs, so a successful injection does minimal damage. Anthropic's version is not to hand it secrets it does not need, run tools in sandboxes, and scope permissions narrowly. OWASP adds that the application should hold its own API tokens and perform privileged functions in code rather than giving them to the model.

**Human confirmation.** OWASP lists human approval for high-risk actions. A person clicking confirm is a check the injected text cannot talk past, provided the confirmation shows the real action and not the model's description of it.

**Output handling.** Treat the model's output as untrusted input to the next component. OWASP recommends specifying output formats and using deterministic code to validate adherence (lesson 11 is the same habit). Its indirect scenario ends with an image linking to an attacker's URL that leaks a conversation, which is an output-rendering failure: a renderer that fetches model-chosen URLs is an exit path, whatever the prompt said.

| Defence | Where it sits | What it buys |
|---|---|---|
| Delimiters, source labels, policy sentence | Prompt | Fewer accidental and naive injections |
| Instruction hierarchy training | Model | Better odds when instructions conflict |
| Input and tool-output screens | System, probabilistic | Catches known patterns, misses new ones |
| Least privilege, sandboxing | System, enforced | Caps the damage of a successful injection |
| Human confirmation | System, enforced | Stops a consequential action |
| Output validation, safe rendering | System, enforced | Stops the output becoming an attack on the next step |

The rows marked enforced are the ones that hold when the model is fooled. The honest summary for a design review is: the prompt makes injection harder, and the system limits what it can do.

## Practice

1. ▢ Which of these changes turns a prompt-level mitigation into a boundary that holds when the model is fooled?

    - a) Adding a system sentence that says the document text is untrusted data
    - b) Wrapping the document in tags and labelling it as an inbound email
    - c) Removing the tool that can send email so the model cannot call it
    - d) Training the team to write the system prompt in clear imperative style

<details markdown="1"><summary>Check</summary>

c). Removing the capability holds even if the model obeys the attacker, because there is nothing to obey with. a) and b) are real but probabilistic: they change what the model is likely to do. d) concerns style and has nothing to do with enforcement.

</details>

2. ▢ Fix this template so it follows the author-side defences from this lesson. Name each change.

    ```text
    Summarise the email. {{email_body}} Do whatever the email asks.
    ```

<details markdown="1"><summary>Check</summary>

Put the email in its own tag, label it ("body of an inbound email from an unknown sender"), escape the value so it cannot close the tag, and state in the system prompt that the email is data that must not override the task. Delete "Do whatever the email asks": it hands the attacker's text the author's authority. These changes lower the odds of a successful injection and do not remove it, so the design still needs the system-side controls below.

</details>

3. ▢ An assistant can read the user's inbox, summarise web pages from links in emails, and render markdown images in its replies. Which trifecta legs are present, and which is the cheapest to remove?

<details markdown="1"><summary>Check</summary>

All three. The inbox is private data, web pages are untrusted content, and a rendered image with a model-chosen URL is a way out. Usually the cheapest leg to cut is the exit: do not render model-supplied image URLs, or allow only an allow-list of hosts. That leaves the model able to summarise and mislead, but not to carry the inbox out of the system.

</details>

4. ▢ A vendor claims its filter blocks 95% of injection attempts. Using the sources in this lesson, say why that does not settle whether to rely on it.

<details markdown="1"><summary>Check</summary>

Willison's point is that in web application security 95% is a failing grade, and he notes there is an unlimited number of ways malicious instructions could be phrased, so a catch rate on known patterns says little about the next phrasing. A filter reduces the rate of known patterns and is worth having, but it is still a probabilistic layer in front of a feature that must be safe when the layer fails. Ask what the worst outcome is on the 5%, and cap that with least privilege.

</details>

5. ▢ A teammate wants to add human confirmation to a feature where the model drafts and sends refund emails. The confirmation dialog shows "Send refund email to customer?" What is wrong with it?

<details markdown="1"><summary>Check</summary>

The dialog shows a description, not the action. If injected text changed the recipient, the amount or the body, the user confirms a sentence that no longer matches what will be sent. A confirmation is only a boundary when it shows the real, final action: the actual recipient, amount and text, produced by code and not summarised by the model.

</details>

## Real-world reps

- [ ] Pick one LLM feature you use or build and write down, for each trifecta leg, whether it is present. If all three are, name the leg you would remove first.
- [ ] Read the "Indirect prompt injection" section of Anthropic's mitigation page and mark which of its bullets are prompt-level and which are system-level.
- [ ] Tomorrow: Check how one product you use renders a link or image in a model reply, and note whether the URL could be chosen by untrusted text.

## Going further

- [Prompt Security](../reference/prompt-security.md)
- [Docs: "Mitigate jailbreaks and prompt injections", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks)
- [Article: "The lethal trifecta for AI agents", Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
- [Paper: "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions", Wallace et al., 2024](https://arxiv.org/abs/2404.13208)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
