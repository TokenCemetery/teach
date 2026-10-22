---
title: Ресурсы
description: "Проверенные источники по промптингу"
type: resources
---

# Ресурсы по промптингу

## Знания

- [Документация: "Prompting best practices", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
  Сводное руководство одного вендора: чёткие инструкции, примеры, XML-теги, роли, размышление, длинный контекст и формат вывода, с промптами «до и после». Использовать для: практической базы для этапов с 2 по 6, читая её как задокументированное поведение одного вендора.
- [Документация: "Prompt engineering overview", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
  Совет определять критерии успеха и тесты до итераций и короткая заметка о том, что не всякий провалившийся eval лучше всего чинить промптингом. Использовать для: привычки сначала измерять.
- [Документация: "Long context prompting", раздел Prompting best practices, Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#long-context-prompting)
  Размещение длинных документов перед запросом, обёртывание каждого в теги с метаданными и просьба сначала привести релевантные цитаты. Использовать для: раскладки длинного ввода.
- [Документация: "Structured outputs", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
  Функция провайдера, которая принудительно применяет к ответу JSON-схему, описанная вместе с тем, чего один промпт не гарантирует. Использовать для: границы между просьбой о структуре и её принудительным обеспечением.
- [Документация: "Prompt caching", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
  Как сопоставляется закешированный префикс, что его инвалидирует и какой порядок должен сохранять промпт, чтобы кеш сработал. Использовать для: раскладки промпта так, чтобы его стабильные части кешировались.
- [Документация: "Model IDs and versioning", Claude Platform Docs](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions)
  Как один вендор называет зафиксированные снапшоты и перемещающиеся псевдонимы и что у каждого идентификатора свой график вывода из эксплуатации. Использовать для: привязки промпта к модели, на которой он тестировался.
- [Документация: "Extended thinking", Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
  Механика API для фазы размышления: бюджет токенов, его минимум и то, как размышление учитывается в лимите вывода. Использовать для: фактов о бюджете, стоящих за промптингом рассуждающей модели; советы по формулировкам есть в руководстве по лучшим практикам.
- [Документация: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
  Превращение вопроса «этот промпт лучше?» в критерии успеха и дизайн eval, включая крайние случаи и сравнение с базовым вариантом. Использовать для: решения, по чему судить изменение промпта, до того как что-либо менять.
- [Документация: "Mitigate jailbreaks and prompt injections", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks)
  Меры защиты на уровне промпта и на уровне системы, включая проверку ввода и ограничение того, что модель может делать. Использовать для: понимания, какие защиты в зоне ответственности автора промпта.
- [Документация: "Prompt design strategies", Gemini API, Google](https://ai.google.dev/gemini-api/docs/prompting-strategies)
  Руководство второго вендора по инструкциям, few-shot-примерам, префиксам и разбиению задачи. Использовать для: проверки, является ли приём общим или поведением одного вендора.
- [Документация: "Chat templates", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
  Как список сообщений с метками ролей превращается в единую последовательность токенов, на которой модель обучалась, с реальным выводом шаблонов. Использовать для: понимания, что модель на самом деле видит.
- [Репозиторий: "Prompt engineering interactive tutorial", Anthropic](https://github.com/anthropics/prompt-eng-interactive-tutorial)
  Упражнения в ноутбуках по ролям, отделению данных от инструкций, примерам, пошаговому рассуждению и недопущению галлюцинаций. Использовать для: практики на этапах с 1 по 4.
- [Статья: "The Prompt Report: A Systematic Survey of Prompting Techniques", Schulhoff et al., 2024](https://arxiv.org/abs/2406.06608)
  Обзор и таксономия приёмов промптинга с единой терминологией. Использовать для: определения места приёма, который вы встретили на практике, и уточнения значения термина.
- [Статья: "Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design", Sclar et al., 2023](https://arxiv.org/abs/2310.11324)
  Показывает, что изменения форматирования, сохраняющие смысл (разделители, регистр, пробелы), сдвигают точность few-shot на большие величины. Использовать для: понимания, почему правка промпта это утверждение, которое нужно проверить, а не вопрос стиля.
- [Статья: "Rethinking the Role of Demonstrations", Min et al., 2022](https://arxiv.org/abs/2202.12837)
  Обнаруживает, что случайная замена меток в демонстрациях почти не вредит, тогда как формат, пространство меток и распределение входов важны. Использовать для: понимания, чему на самом деле учат few-shot-примеры.
- [Статья: "Calibrate Before Use: Improving Few-Shot Performance of Language Models", Zhao et al., 2021](https://arxiv.org/abs/2102.09690)
  Называет смещения к большинству меток, к недавности и к частому токену в few-shot-промптах и предлагает контекстную калибровку. Использовать для: смещений, которые приносит набор примеров.
- [Статья: "Fantastically Ordered Prompts and Where to Find Them", Lu et al., 2021](https://arxiv.org/abs/2104.08786)
  Показывает, что порядок тех же few-shot-примеров качает точность от почти лучшей в своём классе до почти случайной. Использовать для: понимания, почему порядок примеров это переменная, которую нужно контролировать.
- [Статья: "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", Wei et al., 2022](https://arxiv.org/abs/2201.11903)
  Исходный результат по few-shot-цепочке рассуждений и вывод, что выигрыш появляется только при достаточном масштабе модели. Использовать для: понимания, когда просьба о рассуждении помогает.
- [Статья: "Large Language Models are Zero-Shot Reasoners", Kojima et al., 2022](https://arxiv.org/abs/2205.11916)
  Zero-shot-цепочка рассуждений: одна запускающая фраза вызывает рассуждение без примеров. Использовать для: рассуждения без демонстраций, написанных вручную.
- [Статья: "Self-Consistency Improves Chain of Thought Reasoning in Language Models", Wang et al., 2022](https://arxiv.org/abs/2203.11171)
  Сэмплирование нескольких путей рассуждения и выбор ответа большинства. Использовать для: обмена токенов на точность в задаче с одним проверяемым ответом.
- [Статья: "Language Models Don't Always Say What They Think", Turpin et al., 2023](https://arxiv.org/abs/2305.04388)
  Показывает, что в цепочке рассуждений модели отсутствует смещающий признак, который на самом деле определил её ответ. Использовать для: понимания, почему написанное рассуждение не является достоверным объяснением.
- [Статья: "Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models", Tam et al., 2024](https://arxiv.org/abs/2408.02442)
  Измеряет падение точности рассуждения при строгих ограничениях формата вывода. Использовать для: цены принудительного формата и порядка полей.
- [Статья: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
  U-образная кривая: информация в начале и в конце длинного контекста используется лучше, чем информация в середине. Использовать для: решения, куда ставить документы и вопрос.
- [Статья: "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions", Wallace et al., 2024](https://arxiv.org/abs/2404.13208)
  Определяет уровни привилегий системы, пользователя и вывода инструментов и обучает модель при конфликте следовать более высокому. Использовать для: понимания, почему место инструкции меняет её вес.
- [Статья: "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models", Zheng et al., 2023](https://arxiv.org/abs/2311.10054)
  Проверяет 162 персоны в системных промптах на четырёх семействах моделей и 2410 фактических вопросах и не находит улучшения по сравнению с отсутствием персоны, причём эффект персоны в основном случаен. Использовать для: разрешения спора о ролевом промптинге по данным.
- [Статья: "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection", Greshake et al., 2023](https://arxiv.org/abs/2302.12173)
  Вводит косвенную промпт-инъекцию через найденное содержимое и демонстрирует её на реальных приложениях. Использовать для: понимания, как атакующий добирается до промпта, в который никогда ничего не вводит.
- [Статья: "Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs", Ovadia et al., 2023](https://arxiv.org/abs/2312.05934)
  Сравнивает обучение без учителя и поиск как способы добавить знания и находит, что поиск стабильно лучше, и для знаний, встречавшихся при обучении, и для новых фактов. Использовать для: выбора между промптом, RAG и дообучением.
- [Заметка: "LLM01:2025 Prompt Injection", OWASP Gen AI Security Project](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
  Отраслевая запись о риске: прямая и косвенная инъекция, последствия и меры защиты, ранжированные по месту применения. Использовать для: общей терминологии и списка мер защиты.
- [Заметка: "The lethal trifecta for AI agents", Simon Willison](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
  Приватные данные, недоверенное содержимое и канал утечки вместе делают инъекцию эксплуатируемой, а защита состоит в том, чтобы убрать одну из трёх ног. Использовать для: понимания, почему настоящая защита находится вне промпта.
- [Заметка: "Your AI Product Needs Evals", Hamel Husain](https://hamel.dev/blog/posts/evals/)
  Доводы практика в пользу проверок в стиле юнит-тестов и логированных реальных трасс как основы итераций над промптом. Использовать для: построения регрессионного набора из реальных сбоев.

## Пробелы

- Руководства OpenAI по промптингу, рассуждению и структурированному выводу дали бы взгляд третьего вендора, но каждая страница на `platform.openai.com` и `developers.openai.com` ответила 403 и на скриптовую, и на браузерную проверку, поэтому ни одну не удалось подтвердить как доступную. Добавьте их, как только это станет возможно.
- Ни один рецензируемый источник не измеряет практику версионирования промптов или шаблонов напрямую. Уроки 15 и 16 учат ей по документации вендоров и обычной практике разработки ПО и говорят об этом.
