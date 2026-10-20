---
title: Prompting
description: "LLM फ़ीचर के लिए prompts लिखें, version करें और ship करें, साबित करें कि prompt में बदलाव से फ़ायदा हुआ, और किसी और के production prompt की समीक्षा करें"
type: topic
---

# सीखना: Prompting

LLM फ़ीचर के पीछे के prompts इस तरह लिखें कि वे वही करें जो इरादा था, codebase में versioned templates के रूप में रहें, और तभी बदलें जब regression set बताए कि बदलाव से फ़ायदा हुआ। अंत में आप किसी और के production prompt की समीक्षा कर सकें और यह बता सकें कि उसकी हर पसंद की क़ीमत क्या है, बजाय यह कहने के कि वह अजीब लगता है।

**नवीनतम पाठ:** [24. जब आम सलाह ग़लत हो](lessons/0024-when-the-usual-advice-is-wrong.md)

## सफलता कैसी दिखती है

- ऐसा prompt लिखें जिसके roles, instructions और structure को कोई सहकर्मी पढ़ सके और model follow करे, और बता सकें कि model को उससे असल में क्या मिलता है।
- few-shot examples चुनें, क्रम में रखें और जाँचें, और हर पसंद से किस bias का जोखिम है यह बताएँ।
- तय करें कि reasoning कब माँगनी है, reasoning model को standard model से अलग तरह से prompt करें, और समझाएँ कि लिखी हुई reasoning उत्तर की व्याख्या क्यों नहीं है।
- ऐसा structured output पाएँ जिसे program parse कर सके, और लंबे context को ऐसे सजाएँ कि model उसमें मौजूद चीज़ों का इस्तेमाल करे।
- prompts को codebase में versioned templates के रूप में रखें, इस क्रम में कि स्थिर prefix को cache किया जा सके।
- regression set और paired comparison से दिखाएँ कि prompt में बदलाव से फ़ायदा हुआ या नहीं, चंद outputs देखकर राय बनाने के बजाय।
- ऐसा prompt डिज़ाइन करें जो untrusted input को संभाले, और बताएँ कि कौन-से जोखिमों से prompt अकेला नहीं बचा सकता।
- किसी दी गई विफलता के लिए बेहतर prompt, retrieval और fine-tuning में से चुनें, और किसी और के production prompt की समीक्षा उसकी हर पसंद की क़ीमत बताकर करें।

## सीमाएँ

- App-first, chat window से इस्तेमाल लायक: चरण 1 से 6 किसी भी chat interface में चलते हैं, चरण 7 से 10 मानते हैं कि prompt code में रहता है।
- कोई तय provider या model नहीं। Examples provider-neutral हैं; जहाँ कोई technique किसी एक vendor का दस्तावेज़ी व्यवहार है, वहाँ पाठ यह बताता है।
- prompting का पूर्व ज्ञान नहीं माना गया। LLM क्या है, यह "वह अगला token predict करता है" के स्तर पर जानना काफ़ी है।

## दायरे से बाहर

- Retrieve किए गए context पर prompt बनाना और context-window का budget: [`llm/rag`](../../llm/rag/) और उसकी [generation-from-retrieval sheet](../../llm/rag/reference/generation-from-retrieval.md) देखें। यह track सामान्य prompting सिखाता है और retrieval के मामले के लिए वहाँ link करता है।
- Prompt की सतह के रूप में tool descriptions, tools वाले agent में prompt injection, और concurrency में prompt caching: [`llm/agents`](../../llm/agents/) देखें। यह track बिना tools की prompting को कवर करता है और उन पाठों को दोहराने के बजाय link करता है।
- Judge-prompt का डिज़ाइन और eval की methodology: [`llm/evals`](../../llm/evals/) और उसकी [go/no-go sheet](../../llm/evals/reference/go-no-go.md) देखें। यह track prompt में बदलाव मापने के लिए eval का इस्तेमाल करता है, eval बनाना नहीं सिखाता।
- Constrained decoding, यानी structured output का serving वाला पक्ष: [`llm/inference`](../../llm/inference/) देखें। यह track prompt की ओर से structure माँगता है।
- Instruction-following और reasoning को model में कैसे train किया जाता है: [`llm/post-training`](../../llm/post-training/) देखें। यह track बाहर से उनका इस्तेमाल करना कवर करता है।

## पूरी रूपरेखा

दस चरण, model के लिए prompt क्या है यहाँ से लेकर किसी और के prompt की समीक्षा करने की समझ तक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Model के लिए prompt क्या है | 0001 से 0002 | Tokens, chat templates, roles, system prompt और instruction hierarchy | बता सकें कि किसी बातचीत के लिए model को कौन-सा sequence मिलता है और हर instruction कहाँ रखना है |
| 2. Instructions और structure | 0003 से 0005 | स्पष्ट instructions, delimiters और tags, formatting के प्रति संवेदनशीलता | ऐसा prompt लिख सकें जिसे कोई नया व्यक्ति follow कर सके और जो instructions को data से अलग रखे |
| 3. Few-shot examples | 0006 से 0007 | Demonstrations क्या सिखाते हैं, majority-label, recency और ordering biases | Examples चुन और क्रम में रख सकें और हर पसंद से किस bias का जोखिम है यह बता सकें |
| 4. Reasoning | 0008 से 0010 | Chain-of-thought, self-consistency, faithfulness, reasoning models को prompt करना | किसी दिए model और task के लिए तय कर सकें कि reasoning माँगनी है या नहीं, और कैसे |
| 5. Structured output | 0011 से 0012 | Schema माँगना, उसे validate करना, format constraints बनाम reasoning की गुणवत्ता | ऐसा output पाएँ जिसे program parse करे, और उत्तर की गुणवत्ता से उसकी क़ीमत न चुकाएँ |
| 6. लंबा context | 0013 से 0014 | Position के असर, document का layout, quote extraction | लंबे context को ऐसे सजा सकें कि model उसके बीच में मौजूद चीज़ों का भी इस्तेमाल करे |
| 7. Codebase में prompts | 0015 से 0017 | Templates, model snapshot के सामने versioning, prompt caching के लिए layout | Prompts को versioned templates के रूप में रखें, जिनका स्थिर prefix cache हो सके |
| 8. Prompt में बदलाव मापना | 0018 से 0019 | असली विफलताओं से regression sets, noise के सामने paired comparison | एक संख्या से दिखा सकें कि prompt B, prompt A से बेहतर है या नहीं |
| 9. Prompt security | 0020 से 0021 | Direct और indirect prompt injection, prompt किससे बचा सकता है और किससे नहीं | Untrusted input के लिए prompt डिज़ाइन कर सकें और जो जोखिम system पर छूटते हैं उनके नाम बता सकें |
| 10. विवेक | 0022 से 0024 | Prompt बनाम RAG बनाम fine-tune, production prompt की समीक्षा, जिस prompt पर दूसरे निर्भर हैं उसे बदलना, जब आम सलाह ग़लत हो | किसी prompt पर फ़ैसला लेने और उसे किसी और को समझाने के लिए भरोसेमंद |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-what-the-model-sees.md) | Model क्या देखता है | Prompt model तक chat template से बने एक token sequence के रूप में पहुँचता है, इसलिए roles वह formatting हैं जिस पर model को train किया गया है, अलग channels नहीं |
| [0002](lessons/0002-system-prompts-and-roles.md) | System Prompts और Roles | System prompt में क्या आता है और user turn में क्या, और model instructions को उनकी जगह के आधार पर क्रम क्यों देता है |
| [0003](lessons/0003-clear-instructions.md) | स्पष्ट Instructions | ऐसा instruction लिखें जिसे कोई सक्षम नया व्यक्ति follow कर सके: context, task, constraints, और पूरा होना कैसा दिखता है |
| [0004](lessons/0004-structure-and-delimiters.md) | Structure और Delimiters | Instructions को data से tags और sections के ज़रिए अलग करें ताकि model पहचान सके कि कौन-सा क्या है |
| [0005](lessons/0005-format-sensitivity.md) | Format के प्रति संवेदनशीलता | बिना अर्थ वाला formatting बदलाव भी accuracy क्यों हिला सकता है, और इससे हर prompt edit एक ऐसा दावा क्यों बन जाता है जिसे परखना है |
| [0006](lessons/0006-what-examples-teach.md) | Few-Shot Examples क्या सिखाते हैं | Demonstrations ज़्यादातर format, label space और input distribution सिखाते हैं, जिससे उन्हें चुनने का तरीक़ा बदल जाता है |
| [0007](lessons/0007-few-shot-biases.md) | Few-Shot Biases | Few-shot prompts में majority-label, recency और ordering biases, और उनके विरुद्ध examples कैसे चुनें और क्रम दें |
| [0008](lessons/0008-chain-of-thought.md) | Chain-of-Thought | बीच की reasoning माँगना उत्तर कब बेहतर करता है, और कब सिर्फ़ tokens बढ़ाता है |
| [0009](lessons/0009-self-consistency-and-faithfulness.md) | Self-Consistency और Faithfulness | उत्तर पर वोट के लिए कई reasoning paths sample करना, और लिखी हुई reasoning एक faithful व्याख्या क्यों नहीं है |
| [0010](lessons/0010-prompting-reasoning-models.md) | Reasoning Models को Prompt करना | जो model पहले से सोचता है, उसे लिखे हुए चरणों के बजाय लक्ष्य और constraints क्यों चाहिए |
| [0011](lessons/0011-structured-output-from-the-prompt.md) | Prompt से Structured Output | ऐसा output माँगें जिसे program parse कर सके, फिर उसे validate करें, क्योंकि माँगना गारंटी नहीं है |
| [0012](lessons/0012-format-constraints-and-reasoning.md) | Format Constraints और Reasoning | सख़्त output format reasoning की गुणवत्ता की क़ीमत ले सकता है, और fields को कैसे क्रम दें कि उत्तर सोचने के बाद आए |
| [0013](lessons/0013-position-in-long-context.md) | लंबे Context में Position | Model लंबे context के किनारों की जानकारी को बीच की जानकारी से बेहतर इस्तेमाल करते हैं, जिससे तय होता है कि documents और सवाल कहाँ जाएँ |
| [0014](lessons/0014-working-with-long-documents.md) | लंबे Documents के साथ काम | Documents को उनके metadata के साथ tag करें और model से उत्तर देने से पहले quotes निकलवाएँ |
| [0015](lessons/0015-prompt-templates.md) | Prompt Templates | Prompt को एक स्थिर template और हर request पर भरे जाने वाले variables में बाँटें, और untrusted input को structure तोड़ने से रोकें |
| [0016](lessons/0016-versioning-prompts.md) | Prompts की Versioning | Prompt को code की तरह मानें: model snapshot से बँधा, versioned, reviewed और किसी भी दूसरे बदलाव की तरह rollback होने वाला |
| [0017](lessons/0017-prompt-caching-and-layout.md) | Prompt Caching और Layout | Prompt को स्थिर हिस्सों को पहले रखकर क्रम दें ताकि provider prefix को cache कर सके |
| [0018](lessons/0018-a-regression-set-for-a-prompt.md) | Prompt के लिए Regression Set | उन cases का छोटा सेट बनाएँ जिन्हें prompt का बदलाव तोड़ना नहीं चाहिए, असली विफलताओं से शुरू करके |
| [0019](lessons/0019-comparing-two-prompts.md) | दो Prompts की तुलना | Paired comparison से तय करें कि prompt B, prompt A से बेहतर है या नहीं, जो बदलाव को हर run के noise से अलग करती है |
| [0020](lessons/0020-prompt-injection.md) | Prompt Injection | Input का text लेखक के instructions को कैसे override कर सकता है, सीधे या model के पढ़े content में छिपा हुआ |
| [0021](lessons/0021-what-a-prompt-cannot-defend.md) | Prompt किससे नहीं बचा सकता | कौन-से बचाव prompt में आते हैं, और असली बचाव उसमें क्यों रहते हैं जो system model को करने देता है |
| [0022](lessons/0022-prompt-rag-or-fine-tune.md) | Prompt, RAG या Fine-Tune | बेहतर prompt, retrieval और fine-tuning में से इस आधार पर चुनें कि विफलता असल में क्या है |
| [0023](lessons/0023-reviewing-a-production-prompt.md) | Production Prompt की समीक्षा | किसी और के prompt की समीक्षा हर पसंद की क़ीमत बताकर करें, और जिस prompt पर दूसरे निर्भर हैं उसे उन्हें तोड़े बिना बदलें |
| [0024](lessons/0024-when-the-usual-advice-is-wrong.md) | जब आम सलाह ग़लत हो | पहचानें कि किसी model या task के लिए prompting की मानक सलाह कब नाकाम होती है, और विवाद का निपटारा primary source से करें |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत, हर एक के साथ टिप्पणी कि वह क्या कवर करता है
- [Prompt Anatomy](reference/prompt-anatomy.md): roles, क्या कहाँ जाता है, और चरण 1 और 2 की structure checklist
- [Few-Shot और Reasoning](reference/few-shot-and-reasoning.md): examples चुनना और क्रम देना, और reasoning कब माँगनी है, चरण 3 और 4 से
- [Structured Output और लंबा Context](reference/structured-output-and-long-context.md): parse होने लायक output पाना और लंबे inputs को सजाना, चरण 5 और 6 से
- [Production में Prompts](reference/prompts-in-production.md): templates, versioning, cache-friendly layout और माप का चक्र, चरण 7 और 8 से
- [Prompt Security](reference/prompt-security.md): injection के रास्ते और कौन-सा बचाव कहाँ बैठता है, चरण 9 से
- [Prompt Review Checklist](reference/prompt-review-checklist.md): किसी और के prompt से पूछने के सवाल, और prompt बनाम RAG बनाम fine-tune, चरण 10 से

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
