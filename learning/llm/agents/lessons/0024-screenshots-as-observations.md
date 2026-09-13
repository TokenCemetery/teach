---
title: 24. Screenshots as Observations
description: How computer-use agents observe the screen as an image instead of structured data, and why the loop structure still holds
type: lesson
---

# Lesson 24. Screenshots as Observations

**Mission link:** Diagnosing a failing computer-use agent from its trajectory requires understanding that its observations are visual, not structured, so a grounding error looks nothing like a missed tool argument.
**Primary source:** [Docs: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
**Prerequisites:** [Lesson 23](0023-code-execution-as-a-tool.md), [Agent loop](../GLOSSARY.md)

## Warm-up

1. ▢ In earlier lessons, when the agent calls a tool and receives a result, what form does that result take? Is it always structured (JSON or a schema), always unstructured text, or either?

<details markdown="1"><summary>Check</summary>

Structured, in every wire format this track has covered. A tool result is always tagged with the id of the call it answers, and it always carries either the tool's output or an error, even though the exact field names and shape vary by provider and harness (see Lesson 3). The model never has to visually interpret a tool result the way it does a screenshot.

</details>

2. ▢ From Lesson 6: What are the four core steps of the agent loop, in order?

<details markdown="1"><summary>Check</summary>

Call the model, append the response to the transcript, check if done, otherwise execute tools and append their results, then loop back to the start.

</details>

## Know this

### The Observation Changes Type

In earlier lessons, a tool-calling agent's observation after each action is a structured result the harness constructs: a JSON object with fields like `tool_id`, `status`, and `value`. A computer-use agent's observation is radically different. After the agent takes a screen action (click, type, scroll), the observation is a screenshot: literally an image, in PNG or JPEG format, of whatever is displayed on the screen right now.

The model has to visually interpret this image to understand what happened, rather than reading a structured data field. This is a profound shift in how the agent understands the world.

The loop's overall shape from Lesson 6 survives unchanged: send transcript, get response, execute action, append result, repeat. But now "append result" means appending an image to the transcript, and "get response" means the model is generating a description of what it sees in that image and deciding what to do next.

### Why This Matters: Generality

The reason for this design is power. In earlier lessons, a tool-calling agent can only call tools the developer explicitly built for it. If you want an agent to interact with an application that has no API, you have to write a tool that wraps that application's API. But what if the application has no API at all? What if it is only a GUI?

A computer-use agent sidesteps this problem. Instead of needing an API or a custom tool for every application, the agent interacts through the screen, the way a human would. The action space is fixed and generic: move the mouse, click, type text, press keys, scroll, take a screenshot. These same actions work in any GUI application on any operating system, from a web browser to a desktop application to a cloud console. The model learns to do screen things, not application-specific things.

This is the gain: an agent that can operate literally any interface, even ones built without an agent integration in mind.

### The Loop Still Holds

Because the loop structure is conceptually separate from the observation type, the basic cycle survives:

1. Send the transcript (which now includes the current screenshot) to the model.
2. The model looks at the screenshot, understands what is on screen, and decides what to do next.
3. The model emits an action: click at coordinates (x, y), type the string "hello", scroll down, or take another screenshot.
4. The harness executes the action.
5. If the action was a screenshot, the harness appends the new image to the transcript.
6. Loop back to step 1.

The model still decides when to stop, the harness still enforces limits and terminates the loop, the transcript still grows with every turn, and the stopping conditions from Lesson 6 (no more actions, max turns, error threshold) still apply. The only thing that changed is the data type of the observation: from a JSON object to an image.

### Challenges Introduced by Visual Observation

This generality comes with a cost. A structured tool result is unambiguous: the harness built it, it has a fixed schema, and the model can read fields by name. A screenshot is ambiguous: the model has to visually locate what it wants (a button, a text field, a menu item) in the current image, interpret its location, and decide what action to take.

In Lesson 25, you will see this ambiguity crystallize into a specific problem called grounding. For now, know that this trade-off exists: computer-use agents can do things tool-calling agents cannot, because they can operate any GUI, but the observation requires visual interpretation, which introduces new failure modes that structured observations do not have.

## Practice

1. ▢ You are building a computer-use agent to interact with a web application. Your colleague suggests adding a tool called `click_button` that takes a button name as a string argument, so the agent can write `click_button("Submit")` instead of having to deal with coordinates. Is this a good idea? Why or why not?

<details markdown="1"><summary>Check</summary>

It is not. The whole point of a computer-use agent is that it works with any GUI without custom tooling. If you add task-specific tools like `click_button`, you are layering a traditional tool-calling interface on top, which defeats the purpose. The model should learn to take generic actions (click at coordinates, type) and interpret the screenshot visually. Adding wrapper tools adds coupling and reduces the agent's generality.

</details>

2. ▢ A computer-use agent takes a screenshot, sees a login form, and types its username into the password field instead of the username field. Is this a bug in the model, the harness, or the action space itself?

<details markdown="1"><summary>Hint</summary>

The model decided to type the username. The harness executed the action. Something went wrong with connecting the decision to the right part of the screen.

</details>

<details markdown="1"><summary>Check</summary>

This is a visual interpretation error: the model saw the form but misidentified which field was which. The action space (type this string) worked correctly. The harness executed the action correctly. The model's understanding of the screenshot was wrong. This is called a grounding error and is the subject of Lesson 25.

</details>

3. ▢ A tool-calling agent that reads files uses a tool called `read_file(path)` and receives a result with a status field. A computer-use agent that reads files by opening them in a text editor takes a screenshot after opening the editor. Which observation is easier for the harness to verify as successful?

    - a) The tool-calling agent, because the status field is explicit
    - b) The computer-use agent, because a screenshot shows everything
    - c) They are equally easy, just different formats
    - d) Neither, because verifying success requires the model to interpret the result either way

<details markdown="1"><summary>Check</summary>

**a)** The tool-calling agent has an explicit status field; the harness can check `if result.status == "success"` without ambiguity. The computer-use agent's screenshot shows the file contents, but the harness has to take that screenshot to the model and ask it to verify that the file opened correctly, which is slower and less reliable. The observation type affects how easy verification is.

</details>

4. ▢ You are reading a trajectory from a computer-use agent that tried to fill out a form. The agent took eight actions: clicked on fields, typed text, and scrolled. The final screenshot shows the form with empty fields. What should you check first to diagnose why the agent failed?

<details markdown="1"><summary>Check</summary>

Look at the coordinates of each click action against the screenshots taken after each click. Did the agent click on the right part of the screen, or did the clicks land in the wrong places? Even if the model decided to "click on the username field," the actual click coordinate might have been off. This is the grounding problem: the model's intent and the actual screen location diverged.

</details>

## Real-world reps

- [ ] Open a web application in a browser. Take a screenshot manually. For three elements on the screen (a button, a text field, a link), estimate their pixel coordinates (x, y). Now resize the browser window or scroll, take a new screenshot, and re-estimate those same coordinates. Write down how much the coordinates changed and whether a fixed coordinate from the first screenshot would still work on the second one.

- [ ] Read a computer-use agent trajectory (from a public example, a tool documentation, or your own test). Pick one screenshot from the middle of the run. Without looking at subsequent screenshots or actions, write down three things the agent might do next. Then look at the action the agent actually took. Did your predictions match?

- [ ] Tomorrow: Find a description of a computer-use agent failure (in a blog post, GitHub issue, or paper abstract). Before reading the explanation, hypothesize whether the failure was due to the model misunderstanding the task, a tool-call syntax error, a grounding error (wrong coordinates), or something else. Then read the explanation and check whether your guess was right.

## Going further

- [Docs: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
