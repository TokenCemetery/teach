---
title: "3. 工具调用的传输格式"
description: "在你的运行框架与模型服务商之间的协议里，一次工具调用及其结果实际上长什么样"
type: lesson
---

# 第 3 课：工具调用的传输格式

**使命关联:** 为一个给定的任务写出智能体循环，说清上下文里每条消息在做什么，以及什么会让循环结束。
**主要来源:** [文档：“Tool use with Claude”，Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
**前置知识:** [第 2 课](0002-agent-workflow-or-prompt.md)、[工具](../GLOSSARY.md)

## 热身

1. ▢ 运行框架调用模型，与运行框架执行工具，二者有什么区别？

<details markdown="1"><summary>检查</summary>

运行框架调用模型，是通过网络向服务商的 API 发送请求（对话记录加上工具）；模型运行在服务商的基础设施里，并返回结构化的输出。工具则是在模型通过发出结构化的工具调用块来请求它时才被调用；运行框架去执行它，通常是调用同一代码库里或同一网络上的某个函数。

</details>

2. ▢ 在什么情况下，模型可能发送纯文本而不是工具调用？

<details markdown="1"><summary>检查</summary>

当模型已经完成了手头的任务，准备把最终答案返回给用户时；或者当它判断（在你设定的限制之内）这一轮不需要调用工具时。

</details>

## 要点

### 传输中的工具调用

当你向模型服务商发送请求、要求它使用工具时，请求里包含三样东西：模型名称、可用工具的列表（含名称、描述和参数 schema），以及到目前为止的对话记录。

工具定义长这样：一个名称，一段给人读的描述，以及一份约束模型可以发送哪些参数的 JSON Schema。下面是一个只带一个工具的 Anthropic 请求：

```json
{
  "model": "claude-sonnet-5",
  "max_tokens": 1024,
  "tools": [
    {
      "name": "get_weather",
      "description": "Get the current weather for a given city",
      "input_schema": {
        "type": "object",
        "properties": {
          "city": {"type": "string", "description": "The city name"}
        },
        "required": ["city"]
      }
    }
  ],
  "messages": [
    {"role": "user", "content": "What's the weather in Lisbon?"}
  ]
}
```

当模型决定调用一个工具时，它并不会去执行。它返回的是一个结构化的块，描述要调用哪个工具、传什么参数。服务商随即停止输出，并用 `stop_reason` 字段发出这个信号。下面是完整的 Anthropic 响应：

```json
{
  "id": "msg_01ABC",
  "type": "message",
  "role": "assistant",
  "content": [
    {"type": "text", "text": "I'll check that for you."},
    {
      "type": "tool_use",
      "id": "toolu_01XYZ",
      "name": "get_weather",
      "input": {"city": "Lisbon"}
    }
  ],
  "stop_reason": "tool_use"
}
```

注意：`input` 字段已经是解析好的 JSON，而不是字符串。每次工具调用都有唯一的 id（这里是 `toolu_01XYZ`），这样运行框架才能告诉模型哪个结果对应哪次调用。助手也可以在工具调用块之前或之后附带纯文本。

### 从传输到执行

你的运行框架看到这个响应，就知道必须用参数 `{"city": "Lisbon"}` 去执行 `get_weather`。怎么执行，取决于你的工具：

- 如果它是**客户端工具**（你自己代码里的一个函数），就直接调用：`weather_result = get_weather(city="Lisbon")`。
- 如果它是**服务端工具**（由服务商替你运行的东西，比如托管的网页搜索），那么服务商在返回之前已经执行过了。你只需要从响应中取出结果。

### 把结果发回去

运行框架一旦拿到结果（无论是执行函数得到的，还是从服务商的响应中读出的），就把它放进一条新消息发回模型，并标上这次工具调用的 id。Anthropic 的格式把它嵌套在一条 `user` 角色的消息里：

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01XYZ",
      "content": "18C, partly cloudy"
    }
  ]
}
```

这条消息作为新的一轮进入对话记录。模型现在同时拥有它发出的工具调用和结果，并决定下一步做什么：调用另一个工具，用不同的参数再次调用同一个工具，或者返回最终答案。

### OpenAI 的传输格式（差异部分）

OpenAI 的 API 使用相同的概念，但字段名称和结构不同。这里不重复整个交互，只列出差异：

工具参数嵌套在 `function.parameters` 之下，而不是单独的 `input_schema`。模型的工具调用参数以 JSON 编码的字符串形式出现在 `function.arguments` 中，而不是预先解析好的对象，所以你的运行框架必须自己解析它。停止信号是 `finish_reason: "tool_calls"`，而不是 `stop_reason: "tool_use"`。结果以专门的 `role: "tool"` 消息返回，带有 `tool_call_id`，而不是包在 `user` 消息里。下面是用同一个天气任务写的简化示例：

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {"name": "get_weather", "arguments": "{\"city\": \"Lisbon\"}"}
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

随后是作为 `role: "tool"` 消息的结果：

```json
{"role": "tool", "tool_call_id": "call_abc123", "content": "18C, partly cloudy"}
```

模式完全相同：工具定义、带 id 的工具调用、标着同一个 id 的结果。名称和结构不同，但任何能处理其中一种的运行框架，只要把这些字段对应起来，就能适配另一种。

## 练习

1. ▢ 在上面展示的 Anthropic 响应里，为什么 `input` 字段包含的是解析好的 JSON 对象，而不是 JSON 字符串？

<details markdown="1"><summary>检查</summary>

Anthropic 的 API 在服务商一侧就先解析好工具调用的参数再返回，减少了运行框架的工作。你的代码拿到的是可以直接使用的值，而不是需要解析的字符串。OpenAI 发送的则是字符串，所以使用之前，你必须在运行框架里调用 `json.parse()` 或等价的函数。

</details>

2. ▢ 把工具结果发回模型时，为什么要带上 `tool_use_id` 字段？

<details markdown="1"><summary>检查</summary>

模型可能在同一轮里请求了多个工具。这个 id 让模型把每个结果与它发出的对应调用匹配起来，从而知道哪个答案来自哪个请求。

</details>

3. ▢ 在 Anthropic 的协议里，工具结果放在 `user` 角色的消息中传输；在 OpenAI 的协议里，它作为 `role: "tool"` 消息传输。为什么这个差异对智能体循环的逻辑无关紧要？

    - a) 因为运行框架在构建对话记录时不需要区分它们
    - b) 因为不管是什么角色，模型处理它们的方式总是一样的
    - c) 因为其中一种协议显然是错的，应该避免使用
    - d) 因为工具结果不属于正式对话记录的一部分

<details markdown="1"><summary>检查</summary>

**b)** 无论角色标签或消息结构如何，模型处理它们的方式都一样。逻辑是：这是你发出的工具调用的结果，你现在想做什么？协议细节（放在用户消息里，还是作为工具消息）不会改变这个逻辑。(a) 很接近，但没抓住要点：角色对循环本身并不重要。

</details>

4. ▢ 运行框架收到这样一个 OpenAI 响应：`"arguments": "{\"city\": \"Paris\"}"`。在把它传给工具之前，运行框架必须怎样处理？

<details markdown="1"><summary>检查</summary>

把它当作 JSON 解析：`json.loads("{\"city\": \"Paris\"}") yields {"city": "Paris"}`。OpenAI 返回的是字符串，运行框架必须先把它反序列化成字典（或对象），再把参数解包传给函数调用。

</details>

## 实战练习

- [ ] 打开一个真实的智能体框架的代码或文档（LangChain、Vercel AI，或 Claude 自己的 Python SDK），找到它把工具定义发给模型的地方。找出名称、描述和参数 schema，并标出它们在代码中各自来自哪里。
- [ ] 在同一份代码里，追踪完整的一次工具调用周期：找到它在哪里解析模型的工具调用响应、执行工具、把结果发回去。标出它如何用 id 把它们匹配起来。
- [ ] 明天：写一个最小的运行框架（不超过 20 行，伪代码也可以），向模型服务商发送单个工具，解析工具调用响应，再把结果发回去。不要使用框架。

## 延伸阅读

- [文档：“Tool use with Claude”，Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [指南：“Function calling”，OpenAI](https://developers.openai.com/api/docs/guides/function-calling)
- [资源](../RESOURCES.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
