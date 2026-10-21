---
title: "6. 编写循环"
description: "用伪代码构建智能体循环，并有意识地选择停止条件"
type: lesson
---

# 第 6 课：编写循环

**使命关联:** 编写智能体循环是亲手构建智能体的核心技能，直接服务于“为一个给定的任务写出智能体循环，说清上下文里每条消息在做什么，以及什么会让循环结束”这一使命。
**主要来源:** [文章：“Building Effective Agents”，Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
**前置知识:** [第 5 课](0005-parallel-calls-and-errors-as-results.md)、[智能体循环](../GLOSSARY.md)

## 热身

1. ▢ 来自第 5 课：工具调用失败时，什么会被追加到对话记录里？

<details markdown="1"><summary>检查</summary>

一个错误的工具结果，标着失败调用的 id 并标记为错误，追加的方式与成功的结果完全一样。循环不会崩溃；模型把这次失败当作正常的一轮来看待。

</details>

2. ▢ 来自第 5 课：为什么模型同时请求两个工具，而不是一个接一个地请求，是安全的？

<details markdown="1"><summary>检查</summary>

因为每个工具调用都有自己唯一的 id，运行框架返回的每个结果都标着同一个 id。无论执行顺序如何，模型总能把结果对回产生它的那次调用。

</details>

## 要点

### 作为代码的智能体循环

智能体循环的核心很简单。下面是它的伪代码：

```text
function run_agent(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)

    return "Max turns reached"
```

这就是运行框架。模型选择请求哪个工具，以及何时不再请求。运行框架负责强制执行限制和具体的机制。

注意这个结构：**调用模型，追加响应，检查是否完成，否则执行工具并追加它们的结果，然后回到顶部继续循环**。每一轮，对话记录都在增长。对话记录之外，什么都不保存在内存里。

### 为什么每一轮对话记录都必须增长

初学者有时会写出这样的循环：

```text
function run_agent_wrong(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)  # Only append results, not the model's request
```

这是个 bug。如果你在执行工具之前，没有把模型的工具调用响应追加到对话记录里，那么下一轮模型就不会“记得”自己请求过这个工具。运行框架再次调用模型时，对话记录里并没有写着“模型请求了搜索”或“模型请求了计算器”。模型可能会一头雾水地再次请求同一个工具。文献中把这称为遗忘请求。对话记录就此变得前后不连贯。

修复的办法是在调用模型之后**立即**追加响应，先于其他任何事：

```text
function run_agent_correct(model, tools, transcript, max_turns):
    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)  # Append right away

        if response.has_no_tool_calls():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)
            transcript.append(result)
```

现在，循环重复并再次调用模型时，对话记录里包含着“模型说它会调用搜索”，于是模型可以针对结果进行推理。

### 停止条件：有意识地选择

智能体循环需要停下来。有几个地方可以选择：

**最大轮次**：外层循环对轮次计数，超过上限就退出。这是一道安全保护。没有它，出故障的模型或工具循环可能永远运行下去。

**没有工具调用**：模型的响应里不含工具调用。这是“顺利路径”上的停止：模型已经决定作答。在追加了模型的响应之后检查这一点。

**明确的停止工具**：你可以提供一个名为 `stop` 或 `finish` 的工具，模型可以调用它来明确地退出。运行框架检查到它就返回。如果任务是开放式的，模型需要一个明确的“我做完了”动作，这就很有用。如果你提供了这个工具，要把它写清楚，让模型明白什么时候该用。

**错误计数保护**：如果工具调用失败，运行框架会把错误作为结果追加。如果连续失败的工具调用太多，运行框架就会停下来，返回一条错误轨迹，而不是无休止地继续。这可以防止重试循环。

这些并不互斥。生产环境的运行框架可能会把它们全部检查一遍：

```text
function run_agent_with_guards(model, tools, transcript, max_turns, max_errors):
    error_count = 0

    for turn_count in range(max_turns):
        response = call_model(model, transcript)
        transcript.append(response)

        if response.has_no_tool_calls():
            return response.text

        if response.has_explicit_stop_tool_call():
            return response.text

        for tool_call in response.tool_calls:
            result = execute_tool(tools, tool_call)

            if result.is_error():
                error_count += 1
                if error_count > max_errors:
                    return "Too many errors"
            else:
                error_count = 0

            transcript.append(result)

    return "Max turns reached"
```

关键在于，这些决定应该在你的代码里清清楚楚，而不是被隐藏起来或出于偶然。何时停止由你选择，智能体有多少次恢复的机会也由你选择。

## 练习

1. ▢ 在上面展示的伪代码循环里，为什么 `transcript.append(response)` 必须发生在 `if response.has_no_tool_calls()` 检查之前？

<details markdown="1"><summary>检查</summary>

对话记录必须包含模型的响应，这样之后的轮次（或读取轨迹的观察者）才能看到模型说了什么、决定了什么。如果你在追加之前就检查停止，你会返回模型的文本，但对话记录里根本看不出模型作过响应。而且，响应里的其他信息（比如模型考虑过但决定不调用的工具）也会丢失。

</details>

2. ▢ 模型调用了一个工具，运行框架成功执行并返回了结果。结果被追加到对话记录里。下一次循环迭代，运行框架再次调用模型。模型在对话记录里看到了什么是上一轮没看到的？

<details markdown="1"><summary>提示</summary>

想一想上一次循环迭代里，在第一次调用模型之后，追加了什么。

</details>

<details markdown="1"><summary>检查</summary>

模型看到了在循环执行工具之前追加的、它自己的工具调用响应。第二轮时，对话记录里同时有那条响应和工具的结果。如果响应没有先被追加，模型就只会看到结果，仿佛这个工具是被模型之外的某个东西调用的。

</details>

3. ▢ 你在构建一个带最大错误数保护的运行框架：如果连续三个工具调用失败，就停止循环。什么时候需要把错误计数器重置为零？

    - a) 达到最大轮次时
    - b) 工具调用成功并返回了非错误的结果时
    - c) 循环开始时
    - d) 模型的响应里不含工具调用时

<details markdown="1"><summary>检查</summary>

**b)** 工具调用成功时。这道保护是要抓住反复失败的模式。如果一个工具失败了，而下一个成功了，重试循环就被打破了，你想允许更多的失败。如果只在开始时重置 (c)，你就永远无法停止；如果在达到最大轮次或没有工具调用时重置 (a、d)，保护就不起作用。成功时重置才是正确的模式：一次成功就重置计数器。

</details>

4. ▢ 你的模型本应先搜索，读取一份文档，然后做总结。到第三轮，它又请求了同一个搜索工具。第一次搜索是成功的。根据你对对话记录如何工作的了解，你的运行框架里最可能的 bug 是什么？

<details markdown="1"><summary>检查</summary>

运行框架在调用模型之后，没有把模型的工具调用响应追加到对话记录里。模型从未看到自己在第一轮对搜索工具的请求。第三轮调用它时，对话记录里有搜索结果，却没有请求，所以模型不知道这个结果为什么在那里，于是又请求了搜索。修复的办法是在调用模型之后立即追加响应，先于执行工具。

</details>

## 实战练习

- [ ] 不看课程，凭记忆写出基本的智能体循环伪代码。把它与“作为代码的智能体循环”下展示的伪代码对照。检查：你是不是在检查没有工具调用之前，先追加了响应？

- [ ] 在任何开源项目（你用的某个库或某个公开仓库）里找一个智能体的实现。阅读循环代码。找出对话记录是在哪里构建的，以及停止条件是在哪里检查的。注意停止条件是明确的（在 if 语句里一目了然），还是隐藏的（埋在对另一个函数的调用里的某个条件中）。

- [ ] 明天：用伪代码勾画出四个停止条件（最大轮次、没有工具调用、明确停止、错误计数保护）。为每一个写一句话，说明它为什么重要：它解决什么问题？

## 延伸阅读

- [文章：“Building Effective Agents”，Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)
- [资源](../RESOURCES.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
