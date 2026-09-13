---
title: 25. Grounding an Action to a Coordinate
description: Why translating a visual intention into a pixel coordinate is harder and more fragile than a typed tool-call argument
type: lesson
---

# Lesson 25. Grounding an Action to a Coordinate

**Mission link:** Diagnosing a failing computer-use agent requires recognizing grounding errors (a coordinate miss) as distinct from tool misuse or logic errors, so you can fix the right problem.
**Primary source:** [Docs: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
**Prerequisites:** [Lesson 24](0024-screenshots-as-observations.md)

## Warm-up

1. ▢ In a tool-calling agent, when the model wants to update a user, what does it send to the harness, and how does the harness know which specific user to update?

<details markdown="1"><summary>Check</summary>

The model sends a tool call with an argument like `user_id: "u_123"`, a stable, unique identifier. The harness reads this identifier and updates the user by ID with no ambiguity.

</details>

2. ▢ In a computer-use agent, when the model wants to click a button it sees on the screenshot, what does it send to the harness, and how does the harness know which button to click?

<details markdown="1"><summary>Check</summary>

The model sends an action to click at a pixel coordinate, like `click(x=450, y=200)`. The harness reads the coordinate and clicks at that exact position on the screen.

</details>

## Know this

### The Grounding Problem

Grounding is the step of translating a model's intent into an actual screen coordinate. When a tool-calling agent wants to update a record, it specifies the record by a stable ID, a name, or a unique identifier the harness can act on directly. There is no ambiguity: the harness either finds the record or it does not.

When a computer-use agent wants to click a button, it has to visually locate that button in the current screenshot, estimate its pixel coordinates, and emit a coordinate tuple like `(x, y)`. This is harder in four ways.

**First, there is no stable reference.** A button at pixel 450, 200 in one screenshot is a different button (or no button at all) if the window resizes, the page scrolls, or the content shifts. An ID persists across layout changes; a coordinate does not. A tool-calling agent would ask for a button by name; a computer-use agent asks for a button by position, which is fragile.

**Second, the model cannot ask for help.** In a tool-calling agent, if the harness does not understand an argument, it returns a clear error: "user_id u_999 not found" or "invalid format for date_field". The model reads the error and corrects its argument. In a computer-use agent, a click at the wrong coordinate just hits the wrong thing (or empty space). The model does not get an error message. It only finds out on the next screenshot that the click landed in the wrong place, and even then, it has to infer from visual inspection that the click missed.

**Third, the feedback loop is slow.** After a tool-calling agent makes a mistake, it gets a typed error message. After a computer-use agent makes a mistake, it has to take another full screenshot, send it to the model, wait for the model to interpret the new image and reason about what went wrong, and try again. Each grounding error costs a full model round-trip to discover and fix.

**Fourth, small environmental changes break working sequences.** A tool call that names a user by ID still works if the user's name, email, or department changes. A click at coordinates breaks if the button moves even a few pixels. A 13-inch laptop screen, a 27-inch monitor, browser zoom, font rendering, and CSS breakpoints can all move the same button to different coordinates. A trajectory that worked perfectly on one machine might fail silently on another.

### What Makes Grounding Fragile

Imagine an agent successfully clicks a search box at (300, 150) on a desktop browser at normal zoom. The same web page viewed on a mobile phone or with browser zoom set to 125 percent might render the search box at (225, 112) or (375, 188). The coordinate is no longer correct. The click might land on nothing, or on a different element entirely.

The agent's logic was sound. The model made a reasonable decision. The action type (click) was correct. But the coordinate was wrong, because the environment changed. A tool-calling agent that asks for a tool named `search` does not have this problem, since the tool name is stable.

This is why grounding errors are a category of failure unique to screen-driven agents. They do not occur in tool-calling agents, because tool-calling agents reference things by name, not by position.

### Partial Mitigation: Structure Aware Tools

Some browser or computer-use tools try to reduce grounding fragility by offering a middle ground: instead of just a screenshot, the tool also returns structured information about the page's elements: the names, roles, positions, and bounding boxes of every button, link, and form field.

The model can then say "click the button labeled 'Submit'" or "click the text field in the email row", and the harness translates that named reference into a coordinate at click time, rather than asking the model to estimate coordinates from pixels. This recovers some stability: if the button moves, the harness computes new coordinates automatically, without the model having to re-estimate.

This is a trade-off. You gain reliability and lose some of the "works on any GUI" generality that pure screenshot-based action achieves. A structure-aware tool works well for web pages, where HTML elements have semantic roles and stable IDs, but it might not work for desktop GUI applications, games, or obscure applications the tool was not designed for. Pure screenshot-based actions have no this limitation, but they are more fragile.

### How to Spot Grounding Errors in a Trajectory

When you read a computer-use agent trajectory, look for patterns:

- The model's intent makes sense (it decided to search for something, fill out a field, etc.), but the action did not produce the expected result.
- Multiple clicks in a row land in the wrong place.
- The same action works on one screenshot but fails on the next.
- Coordinates are far from any visible element.

These are hallmarks of a grounding error. The model was reasoning correctly about what to do, but the coordinates did not match the screen. This is distinct from a logic error (the model decided to do the wrong thing) or a tool failure (the tool crashed).

## Practice

1. ▢ An agent clicks at coordinates (500, 250) to submit a form. The screenshot before the click shows a Submit button centered at roughly (500, 250). The action succeeds and the form submits. On the next turn, the agent tries to click the same Submit button again at the same coordinates (500, 250), but the form is now gone and a loading message is displayed. The second click lands on nothing. Is this a grounding error?

<details markdown="1"><summary>Check</summary>

No. The first click was correctly grounded. The second click missed because the screen changed, not because the model misestimated the coordinate. Grounding errors happen when the coordinate does not match the intended target on the screenshot the model is looking at right now. Once the page content changed, the coordinate became stale, but that is not a grounding error in the agent's decision-making; it is correct behavior: the agent tried to click on something that was no longer there.

</details>

2. ▢ An agent reads a screenshot of a login page with two fields: username at the top and password below it. The agent decides to type the password, estimates the password field is at approximately (350, 180), and sends the action `type(x=350, y=180)`. The harness clicks at (350, 180), which is actually the username field, and the password gets typed into the username field. The agent then sees a new screenshot showing the username field now filled with the password. Is this a grounding error, a logic error, or both?

<details markdown="1"><summary>Hint</summary>

Ask two questions separately: (1) Did the model make a reasonable decision about what to do? (2) Did the model get the coordinates right?

</details>

<details markdown="1"><summary>Check</summary>

This is a grounding error, not a logic error. The model's decision was correct: it decided to type the password. But the model misestimated the password field's coordinates. The coordinate (350, 180) was wrong; the password field was actually lower on the screen, perhaps at (350, 240). The model intended to click the right target but grounded the action incorrectly.

</details>

3. ▢ A computer-use agent interacts with two different web applications in sequence. On the first application, it successfully fills out a form by clicking on a field at (400, 300). On the second application, it tries to click on a text input field that appears to be in a similar position on the screen, also at (400, 300), but on the second application, that coordinate is empty space and the click lands nowhere. Is the second click a grounding error?

    - a) Yes, because the coordinate did not match the intended target on the second application's screenshot
    - b) No, because the model used the same reasoning for both applications
    - c) No, because the coordinate worked correctly the first time, so the second application must have a UI bug
    - d) No, because grounding errors only happen when the model intentionally tries to click the wrong thing

<details markdown="1"><summary>Check</summary>

**a)** The click was grounded incorrectly: the coordinate did not match the intended target on the second application's current screenshot. The fact that the same coordinate worked on a different application is irrelevant; grounding is about the match between intent and coordinate on the screen in front of the model right now. **b)** is wrong because the model's reasoning is not what makes a click grounded or not, only whether the coordinate lands on the intended target. **c)** is wrong because a coordinate having worked once tells you nothing about whether it is correct on a different screen; the model is the one that assumed stability it should not have. **d)** is wrong because grounding errors are mistakes, not intentional choices.

</details>

4. ▢ You are reading a trajectory where an agent failed to complete a task. In turn seven, the agent clicked at (1200, 50), the top right of the screen. Nothing visible is there, and the click had no effect. The model then said it did not find the button it was looking for. On the next turn, the agent clicked at (150, 50), the top left, and found the button. Formulate a hypothesis about what went wrong in turn seven.

<details markdown="1"><summary>Check</summary>

The agent likely mistook the button's position and grounded the click too far to the right. The button was actually on the left side of the screen, but the model estimated it was on the right. This is a classic grounding error: the model's intent (find and click the button) was right, but the coordinate was wrong. The agent corrected itself on the next turn, possibly by re-reading the screenshot or reconsidering its estimate.

</details>

## Real-world reps

- [ ] Take a screenshot of a web page at normal zoom. Pick a button and write down its pixel coordinates as you estimate them. Now zoom the browser in by 25 percent and take a new screenshot. Look up the same button's coordinates on the zoomed screenshot using your browser's developer tools (inspect the element and check its bounding box). Write down the new coordinates. How far off was your estimate from the actual coordinates on the first screenshot? How did zoom change the position?

- [ ] Watch or read a computer-use agent trajectory (from a blog, tool documentation, or example). For three consecutive actions, compare what the agent intended to do (from the context or prompt) against the coordinates it emitted and the screenshot that followed. Did the grounding match the intention? If not, what changed the coordinates?

- [ ] Tomorrow: Design a simple web form (mentally or in code) that you think would be hard for a computer-use agent to ground correctly. What properties of the form make grounding fragile? Then design a second version of the same form that would be easier to ground, and explain what you changed.

## Going further

- [Docs: "Computer use tool", Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
