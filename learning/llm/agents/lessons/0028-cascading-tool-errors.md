---
title: 28. Cascading Tool Errors and Hallucinated Arguments
description: One tool error leading to wrong decisions, spiraling into confusion, and well-typed but false arguments that schemas cannot catch
type: lesson
---

# Lesson 28. Cascading Tool Errors and Hallucinated Arguments

**Mission link:** Identifying cascading failures and hallucinated arguments in a trajectory allows you to diagnose agent failures at their true origin, breaking the chain before it spirals, rather than patching symptoms downstream.
**Primary source:** [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**Prerequisites:** [Lesson 27](0027-loops-and-context-poisoning.md)

## Warm-up

1. ▢ From Lesson 27: What is the difference between a repetitive loop and context poisoning?

<details markdown="1"><summary>Check</summary>

A repetitive loop is loud: the agent calls the same tool with the same arguments repeatedly, making no progress. Poisoning is quiet: the model states a false or hallucinated fact once, and every later turn silently treats it as established truth.

</details>

2. ▢ From Lesson 4: What does a tool's JSON schema validate?

<details markdown="1"><summary>Check</summary>

A schema validates the structure and type of an argument: that required fields are present, that values match the declared type (string, number, boolean), that lists have the right element type, and that constraints like enum or minLength are met. It does not validate whether the value is true or refers to something real.

</details>

## Know this

### Cascading Failures: One Error Leads to Another

A cascading failure is when one tool error leads to an incorrect follow-up decision, which leads to another error, spiraling away from the task. Each failure compounds the confusion instead of resolving it.

Here is a step-by-step example:

Turn 2: The agent calls search_files(directory="/config") to find a configuration file. The directory does not exist. The tool returns an error: "directory not found".

The harness appends this error to the transcript. So far, so good.

Turn 3: The model reads the error and decides: "The standard home directory does not exist. I must be in a different environment. Let me try /etc/config instead." This is reasonable reasoning based on incomplete information. The model calls search_files(directory="/etc/config").

Turn 4: The search succeeds, but returns results that do not match what the agent is looking for. The model, already committed to the /etc/config path from turn 3, decides: "These results are close enough. I will use the first one." The model now has the wrong file.

Turn 5: The agent reads the wrong file. The content does not match what it expects. Instead of recognizing the mismatch, the model decides: "The file format must have changed. I will parse it with a more lenient approach." The agent continues, still building on the wrong foundation.

Turn 6 through N: Every decision compounds the original error. The agent is now reasoning from a false base and cannot recover without backtracking significantly.

The reason cascading failures happen: when a tool returns an error, the model has to make an assumption about why. Is the directory missing? Is it a permission error? Is the path syntax wrong? The model makes a guess and proceeds. If the guess is wrong, the next tool call is built on that wrong assumption. And the chain goes down from there.

The error-count guard from Lesson 6 will eventually stop the loop, but it stops it after the cascade has grown, not at the origin.

### Hallucinated Arguments: Well-Typed but False

A hallucinated argument is when the model invents a plausible-looking but factually wrong value for a tool argument. The value is well-formed and passes schema validation, but it simply does not correspond to anything real.

This is different from a missing-required-field error (Lesson 3-5). A missing field produces an explicit schema-validation error that the model can see and react to. A hallucinated argument passes validation silently.

Examples:

- The model is supposed to look up a user by username. It calls get_user(username="alice_smith"), but the actual username is "asmith". The schema accepts the string; the call fails downstream because the username does not exist.
- The model needs to call an API endpoint and invents the path: call_api(endpoint="/api/v2/users/search"). The endpoint does not exist, but it looks plausible. The schema validates it as a string; the HTTP call fails with 404.
- The model is asked to call a function by name and invents a name: call_function(name="validate_order"). The function does not exist, but the string is well-formed. The call fails with "function not found" only at runtime.

Why this is worse than a schema validation error: when the schema rejects something (missing field, wrong type), the model gets immediate feedback and can fix it. When an argument is well-typed but false, the error happens downstream, often in cryptic form ("user not found", "404 not found", "function not found"). The model does not immediately understand that its invented value was the problem; it might instead blame the service ("the user database is broken") or the environment ("the API is not running") and make a wrong decision based on that misdiagnosis.

If the cascading failure from the previous section starts with a hallucinated argument, the cascade is worse: the model is building a chain of reasoning on a value it invented and does not know it invented.

### Mitigations: Validation and Echo

The core mitigation is to make hallucinated arguments fail faster and more clearly, and to give the model visibility into what actually happened.

**Validate against a known set**: If a tool takes an argument that should refer to something real (a username, a function name, an endpoint), the tool should validate that it exists. Instead of silently failing downstream, the tool returns an explicit error: "user alice_smith not found; valid users are: alice_s, alice_brown, alicia_m". This gives the model immediate feedback and a set of options to choose from.

**Echo back the resolved value**: After a tool call succeeds, do not just return "success". Return what was actually acted on. Example:

Instead of:
```
Tool result: Success
```

Return:
```
Tool result: Successfully updated order 12345. Order status is now CONFIRMED.
```

This way, if the model's argument was hallucinated but happened to match something unintended, the echo makes the mismatch visible. The model sees "I called with order ID 12345, and the tool reported updating order 12345", and can notice if those match.

**Require explicit confirmation for high-stakes operations**: If a tool call will mutate data or take an action, have the harness ask the model to confirm the actual value before executing. The model sees "you are about to update user username_alice_smith; confirm?" and can catch a hallucination at that point.

### Cascading Failures in the Trajectory

When you read a trajectory and spot a cascade:

1. Identify the first error (turn N): a tool returns an unexpected result or error.
2. Check turn N+1: what assumption did the model make about why the error happened?
3. Trace forward: does the model's next decision follow from that assumption?
4. If the assumption was wrong, the cascade has started.

The diagnostic lesson: the error at turn N is not the problem you should try to fix by re-prompting. The problem is the model's misdiagnosis of the error at turn N+1. Fix the tool to be clearer about what went wrong, or give the model better options to handle that class of error, or tighten stopping conditions so the cascade does not grow.

## Practice

1. ▢ An agent is importing data from a CSV file. On turn three, it calls parse_csv(filename="data.csv"). The tool returns an error: "file not found". On turn four, the model says "The file must be compressed. I will decompress it first" and calls decompress(filename="data.csv.gz"). This tool also fails with "file not found". On turn five, the model tries a different error interpretation: "Maybe the file is in a subdirectory" and calls search_for_file(pattern="data*"). This succeeds and finds "data_backup.csv". On turn six, it parses the backup file, which has different columns than expected, and the parsing succeeds but produces garbage output. Is this a cascading failure, and where did it originate?

<details markdown="1"><summary>Check</summary>

Yes, this is a cascading failure. It originated at turn 3 when the initial parse_csv failed. The model misdiagnosed the error: it assumed the file was compressed or moved, when the real problem was likely just the filename or path. Each turn, the model made a different assumption, and each assumption led to a different action, none of which fixed the underlying problem. By turn 6, the agent is working with the wrong file (data_backup.csv instead of data.csv), and the garbage output is the consequence. The fix is not better reasoning in the model; it is making the initial error message clearer. The tool should return "file data.csv not found in current directory; files found: data_backup.csv, old_data.csv". With that information, the model could have chosen the backup file explicitly on turn 4, instead of going through turns 4 and 5 of misdiagnosis.

</details>

2. ▢ An agent is updating customer records. On turn two, the model calls update_customer(customer_id=987654, status="inactive"). The schema accepts the integer and string. The tool returns "customer not found". On turn three, the model, confused, calls list_customers(). This returns a list of all customers. On turn four, the model picks the first customer from the list and calls update_customer(customer_id=100001, status="inactive"). This succeeds. But the agent was supposed to update customer 987654, not 100001. Why did the hallucinated argument in turn two not produce an obvious error that the model could react to?

<details markdown="1"><summary>Hint</summary>

Think about the difference between a schema validation error and a tool's runtime behavior when given a well-typed but invalid value.

</details>

<details markdown="1"><summary>Check</summary>

The schema did not reject the argument because 987654 is a valid integer. The tool accepted it and looked it up, only to fail at runtime with "customer not found". The error message was clear ("customer not found"), but the model misinterpreted it: instead of concluding "customer 987654 does not exist, I need to find the right ID", it concluded "something is wrong with how I am querying, let me try a different approach". A better tool design would return: "customer 987654 not found; customers exist in the range 100001 to 150000". This makes the mismatch explicit and gives the model a concrete range to work with, preventing the cascade.

</details>

3. ▢ You are building a tool that takes a file path as an argument. The schema says the path must be a string. You expect models to occasionally invent paths that do not exist. Which of these design choices would best prevent hallucinated arguments from creating cascading failures?

    - a) Accept any string path and fail with a generic "file error" when the path does not exist
    - b) Validate the path against a list of allowed directories; reject paths outside the allowed list with a clear error
    - c) Accept any path and return a success message even if the file does not exist, so the model thinks the operation succeeded
    - d) Require the model to pass two arguments: the path and a boolean confirming the path is correct

<details markdown="1"><summary>Check</summary>

**b)** Validate against a list of allowed directories and reject invalid paths with a clear error. This makes hallucinated paths fail fast and explicitly, giving the model immediate feedback. The model can then choose from the allowed list. **a)** still lets the cascade grow because the error is generic and does not help the model understand what went wrong. **c)** is dangerous; it masks the problem and leads to cascades because the model thinks it succeeded when it did not. **d)** requires extra harness logic and does not solve the problem; a model can hallucinate both the path and confirm it anyway.

</details>

4. ▢ An agent is supposed to fetch data from an API. On turn two, it calls fetch_api(endpoint="/api/v1/customers/123"). The endpoint does not exist, and the tool returns a 404 error. On turn three, the model says "The API server must be down" and calls check_service_health(). This returns "service is up and responding". On turn four, the model says "The API must have changed. Let me try without the version number" and calls fetch_api(endpoint="/api/customers/123"). This also fails with a 404. What design change to the first tool would have prevented the cascade?

<details markdown="1"><summary>Check</summary>

The first tool call should have returned more information than just "404 not found". It could return: "endpoint /api/v1/customers/123 not found (404); valid endpoints include: /api/v2/customers/{id}, /api/v2/orders/{id}". With this information, the model would have immediately understood that the version number was wrong, not the service, and it could have adjusted the endpoint on turn 3 instead of turns 3 and 4 of cascade. The cascade happened because the error message did not explain the actual problem.

</details>

## Real-world reps

- [ ] Find an agent trajectory that shows a failure. Read it and identify: is there a cascading chain of decisions, where each decision compounds confusion? If so, at what turn did the cascade originate? What would a clearer error message have done?

- [ ] Design a tool (pick any tool you work with or have designed). Write out an error message the tool currently returns for a common failure case. Now rewrite it to include: what was wrong, what was expected, and what the valid alternatives are. How would this clearer error message change a model's ability to diagnose the problem?

- [ ] Tomorrow: Build a small test harness that calls a tool with a hallucinated argument (a value the tool does not recognize). Observe the error message the tool returns. Then modify the tool to validate against a known set and return a clearer error. Run the same hallucinated argument again and compare the two error messages. Write one paragraph describing how the clearer error would change an agent's diagnosis of the failure.

## Going further

- [Article: "Building Effective Agents", Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
