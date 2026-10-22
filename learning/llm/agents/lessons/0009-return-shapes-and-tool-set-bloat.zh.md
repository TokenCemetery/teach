---
title: "9. 返回形态与工具集膨胀"
description: "工具的返回值要花掉上下文预算，而工具太多会损害模型正确挑选的能力"
type: lesson
---

# 第 9 课：返回形态与工具集膨胀

**使命关联:** 设计智能体的工具面，包括选择工具返回什么（它的返回形态），以及决定提供多少个工具，因为这两者都是设计选择，既影响模型在各个选项中做出正确决定的能力，也影响此后每一轮的成本。
**主要来源:** [文章：“Writing Effective Tools for Agents”，Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
**前置知识:** [第 8 课](0008-naming-and-describing-a-tool.md)

## 热身

1. ▢ 来自第 8 课：为什么工具的描述应当告诉模型何时、如何使用它，而不只是列出它接受哪些参数？

<details markdown="1"><summary>检查</summary>

因为在工具之间做选择时，模型没有别的指引来源。光有参数列表，只说明了怎么调用工具，却没说明为什么、何时该用它，而这才是模型真正要做的决定。

</details>

2. ▢ 来自第 8 课：如果同一工具集里有两个名称和描述非常相似的工具，你会造成什么问题？

<details markdown="1"><summary>检查</summary>

模型无法可靠地区分它们，所以可能调用错的那个，或为保险起见两个都调用。这种噪声还会削弱模型在集合中所有其他工具之间做出正确选择的能力，而不只是那两个相似的工具。

</details>

## 要点

### 工具的返回值要花掉上下文预算

对话记录里的每条消息都会消耗 token。工具返回结果时，这个结果会被追加到对话记录里，模型在之后的每一轮都会看到它，直到运行结束，或对话记录被截断。返回一个小而聚焦的答案的工具，代价很小。返回五千行数据库记录的工具，在这次运行余下的每一轮都要花掉实实在在的 token，不管模型是否需要其中的全部。

```text
Bad:
Tool: fetch_user_records
Returns: [complete User record, complete User record, ...]
# 5000 rows, 50KB of JSON, ~10,000 tokens consumed per turn after this call
```

工具返回之后，对话记录急剧膨胀。模型在下一轮光是为了读自己的上下文，就得处理全部五千行。这既挤占了 token 预算，又拖慢了循环。

### 为决策而设计返回形态，而不是为完整性

不要把底层系统有的东西全部返回，而要设计一种返回形态，给模型决定下一步所需要的东西。

```text
Better: Option 1 - Return a summary
Tool: fetch_user_records
Returns:
  total_count: 5000
  sample_results: [User, User, User, ...] # top 5 results
  query_was_too_broad: true
  suggestion: "Your query matches 5000 users. Narrow it with a company_id or email domain filter."

# ~500 tokens consumed per turn after this call
```

模型现在能看出查询范围太宽，也知道接下来该做什么：用更好的过滤条件再次调用这个工具。这只用了完整转储十分之一的 token。

```text
Better: Option 2 - Let the model ask for more
Tool: fetch_user_records
Returns:
  count: 50  # number of results returned
  total_matching: 5000  # number of results if the query was not limited
  results: [User, User, ...] # just the first 50
  next_page_token: "abc123xyz"

# Model sees it got 50 of 5000. It can decide to refine the query or ask for the next page.
```

两种情况下，模型都拿到了足够的信息来做出有依据的决定，又不会被数据淹没。

### 工具集膨胀：工具越多，选择越差

给智能体加一个工具并不是免费的。模型可以选择的每个工具，都会让模型的选择更困难。这称为工具集膨胀。

只有三个工具时，模型大多数时候都能选对：

```text
Tools:
- search_documentation
- read_file
- list_directory
```

有十个工具时，模型开始自我怀疑，明明一个就够，却调用多个工具：

```text
Tools:
- search_documentation
- search_issues
- search_code
- read_file
- read_logs
- list_directory
- list_repos
- get_git_history
- get_git_diff
- get_git_status
```

每增加一个新工具，都会给决策添加噪声。模型在挑选之前，得读完并考虑全部十条描述。如果有两个相似（search_code 和 search_documentation），模型可能两个都调用。这种影响是悄无声息的：每个已有的工具都会受到一点损害，而不只是新工具。

代价是实实在在的：更多的工具调用，对话记录里更多的 token，更多的轮次浪费在多余的信息上。

### 新增一个工具，还是新增一个参数

当你想加一个工具时，先问问：这能不能作为现有工具上的一个参数？

```text
Bad: Two tools
- name: list_files
- name: list_directories
```

更好：一个带参数的工具

```text
Good: One tool with a parameter
- name: list_contents
  parameters:
    - name: path
    - name: type
      type: enum
      values: [files, directories, all]
```

模型选择它想要的类型，而你没有给工具集增添噪声。

但有时新增工具是合理的。如果这些工具在根本上不同（调用的情境不同，返回的形态不同，需要的权限不同），那么一个名称清晰的新工具，比一个被塞得过多的参数更好：

```text
Good: Two specialized tools
- name: search_database_by_id
  parameters:
    - id
    # Fast, returns a single record
- name: search_database_by_query
  parameters:
    - query
    # Might return many records
```

模型知道其中的区别：by_id 快而精确，by_query 灵活但可能返回很多。名称让这个决定一目了然。

规则是：当调用这个工具的原因在根本上不同，或者你无法用参数来表达这种区别时，就新增一个工具。当工具基本上是同一个操作，只是输入或输出格式有所变化时，就新增一个参数。

### 在实践中观察工具集膨胀

一个微妙的迹象是，模型开始说出类似“我应该先调用 search 看看它是否存在，如果存在再 fetch”这样的话，而其实一个工具就能完成整个工作。这是模型在求稳，因为它对每个工具做什么没有把握。问题不在模型，而在工具集。

另一个迹象是重复的工具调用：模型在一次运行里多次调用同一个工具，比如搜索两次，或者列出两次。这通常意味着工具集没有给模型在一次调用里缩小结果范围的办法，所以它只能用不同的参数反复调用这个工具，才能找到它需要的东西。

## 练习

1. ▢ 一个叫 `get_user_history` 的工具，返回过去一个月 100,000 条用户操作事件的 JSON 数组，每条都很详细。模型多半会调用这个工具，看前十条事件，然后忽略其余的。做什么样的设计改动，能减少这次调用之后每一轮的 token 成本？

<details markdown="1"><summary>检查</summary>

把返回限制在前 N 条事件（例如前 20 条），并附上 total_count，以及让模型要求更多的办法。这样模型能看到它需要的东西，又不必为全部 100,000 条事件付出代价。另一种办法是返回摘要：“过去一周 50 条事件，前一周 50 条。最近一条：用户登录”，而不是完整的细节，需要具体内容时再让模型去要。

</details>

2. ▢ 你有一个包含 15 个工具的工具集。模型在同一次运行里同时调用了 search_by_name 和 search_by_id，尽管这两种搜索本可以表达为单个工具的参数。把它们保留为两个独立的工具，有什么害处？

<details markdown="1"><summary>提示</summary>

想想模型的工作：它得读十五条描述，并决定调用哪个工具。有相似的工具，是怎样让这项工作更困难的？

</details>

<details markdown="1"><summary>检查</summary>

工具集膨胀。模型要在十五个工具中做选择。像 search_by_name 和 search_by_id 这样相似的工具，让选择更困难。模型可能明明一个就够，却两个都调用，或者浪费时间去判断哪个合适。因为集合变得更嘈杂，每个已有的工具都会受到一点点损害。修复的办法是把它们合并成一个搜索工具，用一个参数来指定搜索的字段。

</details>

3. ▢ 下面哪一项表明工具的返回形态过于冗长？

    - a) 这个工具被调用得非常频繁
    - b) 模型读完结果后，要求先做个摘要再使用
    - c) 这个工具执行要花很长时间
    - d) 这个工具需要身份验证

<details markdown="1"><summary>检查</summary>

**b)** 模型读完结果后，要求先做个摘要再使用。这说明工具返回的信息太多了；模型得先过滤或总结拿到的东西，才能做出决定。(a) 与返回形态无关；被频繁调用的工具可能本来就设计得很窄。(c) 说的是执行速度，而不是 token。(d) 说的是权限，而不是返回形态。

</details>

4. ▢ 你在为代码搜索智能体设计工具。`search_code` 和 `get_code_diff` 应该是一个工具，还是两个？用一两句话说明。

<details markdown="1"><summary>检查</summary>

两个独立的工具。它们被调用的原因不同（搜索是找出匹配某个模式的文件，diff 是展示不同版本之间的变化），返回的形态不同（文件列表与结构化的 diff），解决的问题也不同。一个被塞得过多的工具会让模型的选择更困难。如果它们是同一个操作的变体（比如带有不同查询参数的 search_code），就可以做成带参数的一个工具。

</details>

## 实战练习

- [ ] 在你能接触到的某个 LLM 应用或智能体里，找出它的工具集。数一数工具的数量。读模型的轨迹，标出模型调用工具的每一轮。估计一下：模型有没有在一个工具就够用的时候，调用了两个相似的工具？用一句话写下你觉得这个工具集是膨胀了还是设计得当。

- [ ] 挑一个返回结构化数据的工具。读一个示例返回值。返回里有没有哪部分是模型多半会忽略的？改写返回形态，去掉那部分数据，或把它挪到第二次调用里，并估计你节省了多少 token。

- [ ] 明天：设计一个两种做法都说得通的工具（新增工具，或在现有工具上加一个参数）。针对你的选择，写两句话，说明你为什么选了独立的工具或者参数，另一种做法会付出什么代价，以及什么时候你会重新考虑。

## 延伸阅读

- [文章：“Writing Effective Tools for Agents”，Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [资源](../RESOURCES.md)

---

没学明白？请重读顶部的主要来源，因为本课是对它的压缩，而理解正是在压缩中流失的。如果有哪个术语觉得含糊，可以查看[术语表](../GLOSSARY.md)。

如果问题出在课程本身，而不是学习材料，那就是一个缺陷：[提交 issue](https://github.com/TokenCemetery/teach/issues)。
