---
title: "8. 为工具命名与撰写描述"
description: "工具的名称和描述是模型用来决定何时调用、如何调用它的依据"
type: lesson
---

# 第 8 课：为工具命名与撰写描述

**使命关联:** 设计智能体的工具面（名称、描述、返回形态，以及决定它无人看管时可以做什么的权限边界），要从理解这一点开始：名称和描述并不是写给人看的 API 文档，而是模型用来决定何时、如何调用工具的提示词界面。
**主要来源:** [文章：“Writing Effective Tools for Agents”，Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
**前置知识:** [第 7 课](0007-the-transcript-as-state.md)、[工具](../GLOSSARY.md)

## 热身

1. ▢ 来自第 7 课：模型是如何“记住”智能体循环上一轮发生了什么的？

<details markdown="1"><summary>检查</summary>

它并不会独立地记忆。运行框架在每次调用时都会重新发送完整的对话记录，所以看起来像记忆的东西，其实是模型在重读它之前看到的一切。

</details>

2. ▢ 来自第 7 课：为什么对话记录是智能体的全部状态，而不是运行框架另外保存的某种其他数据结构？

<details markdown="1"><summary>检查</summary>

因为模型只看得到对话记录。运行框架知道、却从未追加进去的任何事实，对模型都是不可见的，不管运行框架在内部还跟踪着什么。

</details>

## 要点

### 工具描述不是 API 文档

每个构建者都会犯一次的错误：像写 REST 端点的文档字符串那样，去写工具描述。

```text
Bad:
name: fetch_user
description: Fetches user data
```

对于要在几个工具之间做选择的模型来说，这太简略了。模型无从得知什么时候该用 `fetch_user`，什么时候该用 `get_user` 或 `lookup_user`。它不知道会返回什么数据，也不知道要传入什么。它无法判断该现在调用，还是以后再调用。当模型看到三个工具、却没有明确的指引时，它只能猜，而且猜错的次数比人更多。

下面是为模型而写的同一个工具的描述：

```text
Better:
name: fetch_user
description: Look up a user profile by their numeric ID. Returns the user's name, email, account status, and the current version number of their profile. Use this before calling update_user, since update_user requires you to pass the profile's current version number to prevent write conflicts. Returns null if the user ID does not exist.
```

现在模型能看到全貌：什么时候调用它（在 update_user 之前），它需要什么（一个数字 ID），以及它会给回什么（足以决定下一步的信息）。这段描述服务的是模型的决策，而不是读 API 文档的人。

区别在于：REST 的文档字符串告诉人类程序员如何使用一个工具。智能体提示词里的工具描述，则告诉模型何时、为何调用工具，要传什么，以及预期得到什么结果。模型没有手册；你的描述是它唯一的向导。

### 与其他工具明确区分的命名

模型只靠阅读名称和描述，没有其他信号，在工具之间做选择。如果两个工具听起来很像，模型就会调用错的那个，或者为保险起见两个都调用。

```text
Bad:
- name: list_files
  description: Lists files in a directory
- name: list_file_contents
  description: Lists the contents of a file
```

模型可能会把这两个搞混，或者明明只需要一个却两个都调用。这两个名称太接近了。

```text
Better:
- name: list_directory
  description: List all files and subdirectories in a directory. Shows names and file sizes. Does not show file contents.
- name: read_file
  description: Read the complete contents of a single file. Returns text as a string.
```

现在名称有了区别（list_directory 对 read_file），描述也清楚地说明了每个工具做什么、不做什么。模型会选对。

规则是：工具的名称应该说明它做什么，而且不会与同一工具集里的任何其他工具混淆。如果你有多个搜索工具，不要把它们都叫 `search`。把它们叫作 `search_documentation`、`search_code`、`search_logs`。

### 参数描述同样重要

顶层的工具描述最受关注，但参数描述对正确性同样重要。

```text
Bad:
name: create_issue
description: Creates a GitHub issue
parameters:
  - name: title
    type: string
    description: Issue title
  - name: body
    type: string
    description: Issue body
```

模型不知道标题应该是什么格式、可以多长、应该是疑问句还是陈述句。正文更糟：是 Markdown 吗？纯文本吗？要多详细？模型该描述问题，还是描述解决方案？

```text
Better:
name: create_issue
description: Create a new issue in the repository
parameters:
  - name: title
    type: string
    description: A one-line summary of the problem or feature request. Be specific and actionable. Examples: "Handle null config values in startup" or "Add support for JSON output format".
  - name: body
    type: string
    description: Detailed description in Markdown. Include what you tried, what failed, and what you expect to happen. If it is a feature request, explain why it matters. If it is a bug, include steps to reproduce.
```

现在模型知道该写什么样的标题，以及正文该包含多详细的内容。它会产出更好的结果。

### 一种常见的失败：相似的工具让模型混淆

最糟的情况是，两个工具相似到即使有描述，模型也分不清它们。

```text
Very bad:
- name: update_user
  description: Update user information
- name: change_user
  description: Modify user data
```

这些名称和描述说的几乎是同一件事。模型可能两个都调用，或者调用错的那个，或者浪费时间去询问。你没有给它任何选择的依据。

修复的办法是，让名称和描述的差异大到对眼前的任务来说只有一个说得通：

```text
Better:
- name: update_user_profile
  description: Change a user's displayed name, email, or profile picture. Requires the profile version number to prevent conflicts.
- name: update_user_permissions
  description: Grant or revoke access roles for a user, such as admin, editor, or viewer. Only callable by the current account's admin.
```

现在模型能看出，第一个工具用于个人信息，第二个用于访问控制。它会选对。

## 练习

1. ▢ 你有两个工具：`send_email` 和 `send_notification`。模型有时明明只需要一个，却两个都调用。为每个工具各写一句话，让模型清楚该用哪一个、什么时候用。

<details markdown="1"><summary>检查</summary>

可能的答案：`send_email` 可以是“向某个电子邮件地址发送一封邮件。用于超过几行的消息，或者需要附件或格式化文本时。”`send_notification` 可以是“向用户发送一条简短的应用内通知。用于不需要用户离开应用的简短状态更新或提醒。”关键在于，描述要告诉模型每个工具期望的是什么样的消息，这样它才能选对。

</details>

2. ▢ 你的 `get_user` 工具返回用户记录里的所有字段：id、姓名、邮箱、电话、地址、公司、简介、偏好、订阅等级，还有另外十个。参数描述应当指导模型该传什么。描述里不该放什么？

<details markdown="1"><summary>提示</summary>

想一想，模型要正确调用这个工具需要知道什么，而什么是知道了不错、但调用本身并不需要的。

</details>

<details markdown="1"><summary>检查</summary>

不该把工具返回的每个字段都列出来。工具的描述说明模型会拿回什么；参数的描述说明模型调用它时必须提供什么。对于 `user_id` 参数，描述应该类似于“用户的数字 ID。如果你没有这个 ID，先调用 search_users。”不要在参数描述里列出返回哪些字段；那应放在顶层的工具描述里。

</details>

3. ▢ 下面哪一项是为工具的参数写详细描述的最佳理由？

    - a) 为了符合 API 文档的标准
    - b) 为了帮助以后阅读代码的工程师
    - c) 为了帮助模型决定传什么值，以及到底要不要调用这个工具
    - d) 为了减少用户需要发起的工具调用次数

<details markdown="1"><summary>检查</summary>

**c)** 为了帮助模型决定传什么值，以及到底要不要调用这个工具。模型阅读参数描述，来理解工具期望什么参数，以及传错了值会发生什么。(a) 无关；这是提示词工程，而不是 API 设计。(b) 可能是附带的好处，但不是首要原因。(d) 没抓住要点：详细的描述帮助模型减少错误的调用，而不是减少调用的总数。

</details>

4. ▢ 你在构建一个叫 `search` 的工具。你还有名为 `search_documents`、`search_issues` 和 `search_users` 的工具。为什么这样给工具命名是个问题，你应该怎么做？

<details markdown="1"><summary>检查</summary>

`search` 这个工具太笼统了。模型需要搜索时，不知道该调用哪个搜索工具。它可能全部调用，或者随机挑一个。应该把 `search` 改名为更具体的名称，比如 `search_logs`、`search_comments` 或 `search_code`。规则是：每个工具的名称要具体到让模型知道它做什么，并且与其他工具的名称有足够的区别，让模型不会把它们搞混。

</details>

## 实战练习

- [ ] 找出你所用的某个 LLM 应用或智能体框架的工具定义（名称和描述）。阅读每个工具的描述。写下一个描述足够清楚、让你明白模型该在什么时候调用的工具，以及一个描述过于含糊的工具。记下前者为什么奏效，以及后者缺了什么。

- [ ] 挑一个你在命令行里经常用的工具（比如 `grep` 或 `find`）。设想你必须为一个对你的文件系统一无所知的模型来描述它。写一句描述，告诉模型这个工具做什么，以及什么时候该用它而不是类似的工具。

- [ ] 明天：从真实的智能体或 API 文档里，挑一份你认为写得不好的工具描述。为一个要在几个相似工具之间做选择的模型改写它。让它至少长一倍，加入一个说明何时使用的例子，并说出它不适合做的一件事。

## 延伸阅读

- [文章：“Writing Effective Tools for Agents”，Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [资源](../RESOURCES.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
