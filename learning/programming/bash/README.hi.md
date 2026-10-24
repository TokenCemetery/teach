---
title: Bash
description: "ऐसा shell लिखें जो production में टिका रहे: quoting, exit status, failure modes, और यह जानना कि कब रुककर असली भाषा इस्तेमाल करें"
type: topic
---

# सीखना: Bash

CI pipelines, deployment और operational tooling के लिए ऐसे shell scripts लिख और संभाल सकें जो ख़राब input या unset variable पर चुपचाप न टूटें, और पहचान सकें कि कब कोई script shell से बड़ी हो गई है और उसकी जगह असली भाषा में है।

**नवीनतम पाठ:** [17. shellcheck, shfmt, और Script की Testing](lessons/0017-shellcheck-shfmt-and-testing-a-script.md)

## सफलता कैसी दिखती है

- ऐसी CI/deployment script या operational utility लिखें जो quoting, exit status और आम failure modes को सही ढंग से संभाले, और समझाएँ कि हर चुनाव क्यों ज़रूरी था।
- किसी shell script को देखकर उस ख़ास तरीक़े का नाम बताएँ जिससे वह किसी edge case पर टूटेगी (unquoted expansion, unset variable, किसी command के exit status को अनदेखा करना)।
- पहचानें कि कब कोई script shell के विवेक-मुक्त दायरे से बड़ी हो गई है, और बताएँ कि वह काम अब `programming/python` में क्यों होना चाहिए।

## सीमाएँ

- Shell scripting का कोई पूर्व अनुभव नहीं माना गया है।
- Bash-only idioms के बजाय POSIX `sh` portability के लिए लिखा गया है, भले ही इस विषय का घर bash है; bash-only feature इस्तेमाल होने पर उसे साफ़ तौर पर ऐसा बताया जाता है।
- `awk`/`sed` को सिर्फ़ वहीं छुआ गया है जहाँ script को सचमुच उनकी ज़रूरत है, अपने-आप में विषय के रूप में नहीं।

## दायरे से बाहर

- वह सब कुछ जो उस बिंदु के बाद आता है जहाँ script को shell नहीं रहना चाहिए था: उस सीमा के लिए [`programming/python`](../../programming/python/) देखें।

## पूरी रूपरेखा

ग्यारह चरण, quoting से लेकर shellcheck, shfmt और testing तक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Quoting | 0001 | वह एक आदत जो production में shell scripts के टूटने के सबसे आम तरीक़े को रोकती है | सही ढंग से quote कर सकें और समझा सकें कि unquoted expansion क्यों टूटता है |
| 2. Exit status और error handling | 0002 से 0003 | `$?`, अनौपचारिक strict mode (`set -euo pipefail`), `trap` | ऐसी script लिख सकें जो exit status और failure को सही ढंग से संभाले |
| 3. Word splitting और globbing के जाल | 0004 | Bash Pitfalls सूची, quoting से आगे के आम footguns | किसी script को देखकर उस ख़ास edge case का नाम बता सकें जिस पर वह टूटेगी |
| 4. Portability | 0005 | POSIX `sh` बनाम bash-only idioms, हर एक कब मायने रखता है | Portable `sh` लिख सकें और bash-only feature को साफ़ तौर पर बता सकें |
| 5. ज़रूरत पड़ने पर `awk`/`sed` | 0006 | हर एक को सिर्फ़ वहीं इस्तेमाल करना जहाँ script को सचमुच उसकी ज़रूरत हो | असली ज़रूरत के लिए `awk`/`sed` उठा सकें, उनका ज़रूरत से ज़्यादा इस्तेमाल किए बिना |
| 6. कब रुकना है यह जानना | 0007 | पहचानना कि shell अपने विवेक-मुक्त दायरे से बड़ी हो गई है | बता सकें कि कोई दिया गया काम अब `programming/python` में क्यों होना चाहिए |
| 7. Shell की बुनियादी बातें | 0008 से 0009 | Variables, command substitution, control flow (`if`/`case`/loops), functions, `local`, return status बनाम output | Variables, command substitution और control flow से script लिख सकें, और दोहराए जाने वाले काम को सही दायरे वाले functions में व्यवस्थित कर सकें |
| 8. Parameter expansion और arrays | 0010 से 0011 | Unset पर default या error (`${v:-}`, `${v:?}`), काट-छाँट (`${v%%}`), substitution, indexed और associative arrays | किसी मान को inline ही default, validate और transform कर सकें, और list या map को string में encode किए बिना रख सकें |
| 9. Redirection और composition | 0012 से 0013 | Redirection का क्रम, file descriptors, here-docs, piped `while` loop अपने variables क्यों खो देता है, process substitution | Streams को सही ढंग से redirect कर सकें और समझा सकें कि piped loop के भीतर set किया गया variable उसके बाद क्यों नहीं बचता |
| 10. Arguments और job control | 0014 से 0015 | `getopts`, usage/help की परिपाटी, signals, background jobs, `wait` | Script के अपने flags और arguments parse कर सकें, और background काम और अपने shutdown को सही ढंग से संभाल सकें |
| 11. Safety और tooling | 0016 से 0017 | `mktemp`, `eval`/injection की सतह, ShellCheck, `shfmt`, bats/shunit2 से testing | Temp files और dynamic commands सुरक्षित ढंग से बना सकें, और static analysis और tests से वह पकड़ सकें जो अकेली समीक्षा चूक जाती |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-quoting.md) | Quoting | वह एक आदत जो production में shell scripts के टूटने के सबसे आम तरीक़े को रोकती है |
| [0002](lessons/0002-exit-status.md) | Exit Status | $? असल में क्या report करता है, bash default रूप से विफल command के बाद भी चलता क्यों रहता है, और production में script के टूटने का दूसरा सबसे आम तरीक़ा |
| [0003](lessons/0003-strict-mode-and-trap.md) | Strict Mode और trap | set -euo pipefail का हर flag असल में क्या बदलता है, उसकी असली कमियाँ, और script fail होने पर भरोसेमंद ढंग से सफ़ाई के लिए trap का इस्तेमाल |
| [0004](lessons/0004-word-splitting-and-globbing-pitfalls.md) | Word Splitting और Globbing के जाल | एक छूटे quote से आगे के आम footguns, जहाँ अकेली quoting पूरा सुधार नहीं है |
| [0005](lessons/0005-portability.md) | Portability | POSIX sh असल में क्या गारंटी देता है, bash की कौन-सी आम features उसका हिस्सा नहीं हैं, और यह फ़र्क़ असल में कब मायने रखता है |
| [0006](lessons/0006-awk-and-sed-where-needed.md) | ज़रूरत पड़ने पर awk और sed | उस काम का आकार पहचानना जिसमें sed और awk हर एक फ़िट होता है, और आदतन नहीं, सिर्फ़ तब किसी एक को उठाना जब script को सचमुच उसकी ज़रूरत हो |
| [0007](lessons/0007-knowing-when-to-stop.md) | कब रुकना है यह जानना | वे ठोस संकेत कि कोई script shell के विवेक-मुक्त दायरे से बड़ी हो गई है, और वह काम अब असली भाषा में क्यों होना चाहिए |
| [0008](lessons/0008-variables-command-substitution-and-control-flow.md) | Variables, Command Substitution, और Control Flow | मान रखने, command का output पकड़ने, और उस पर branch या loop करने के लिए shell की अपनी शब्दावली |
| [0009](lessons/0009-functions-local-and-return-status-vs-output.md) | Functions, local, और Return Status बनाम Output | दोहराए जाने वाले काम को function में व्यवस्थित करना, और वह सबसे तीखी बात जो shell function लगभग हर दूसरी भाषा के function से अलग करता है |
| [0010](lessons/0010-parameter-expansion.md) | Parameter Expansion | अलग command उठाए बिना, किसी मान को inline ही default करना, उस पर error देना, और उसकी काट-छाँट करना |
| [0011](lessons/0011-arrays.md) | Arrays (Indexed और Associative) | संरचना को string में encode किए बिना एक से ज़्यादा मान रखना, और वह एक quoting रूप जो हर element को सही-सलामत रखता है |
| [0012](lessons/0012-redirection-file-descriptors-and-here-docs.md) | Redirection, File Descriptors, और Here-Docs | Command के output को screen के अलावा कहीं और, सटीक रूप से, भेजना, और उसे inline input का एक block देना |
| [0013](lessons/0013-pipes-subshells-and-process-substitution.md) | Pipes, Subshells, और Process Substitution | Piped loop के भीतर set किया गया variable pipe ख़त्म होते ही क्यों ग़ायब हो जाता है, और वह bash-only सुधार जो उसे बचाए रखता है |
| [0014](lessons/0014-argument-parsing-with-getopts.md) | getopts और Usage परिपाटी के साथ Argument Parsing | Script के अपने flags और arguments को उसी अनुशासित ढंग से parse करना जैसे उसे बाक़ी सब कुछ parse करना चाहिए |
| [0015](lessons/0015-signals-background-jobs-and-wait.md) | Signals, Background Jobs, और wait | एक script के भीतर काम को concurrently चलाना, और यह पक्का करना कि script का अपना shutdown उसे अनाथ न छोड़ दे |
| [0016](lessons/0016-mktemp-safe-temp-files-and-the-eval-injection-surface.md) | mktemp, सुरक्षित Temp Files, और eval/Injection की सतह | ऐसी temporary file बनाना जिसका अनुमान या अपहरण न हो सके, और eval untrusted input को मनमाने code में क्यों बदल देता है |
| [0017](lessons/0017-shellcheck-shfmt-and-testing-a-script.md) | shellcheck, shfmt, और Script की Testing | वह tool जो script की ज़्यादातर चुपचाप टूटनों को उसके चलने से पहले ही पकड़ लेता है, और बाक़ी को test कैसे करें |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत
- [Quoting और जाल](reference/quoting-and-pitfalls.md): quoting का नियम, वह कहाँ काटता है, और वे Bash Pitfalls जो सावधान quoting के बाद भी बचे रहते हैं
- [Exit Status और Error Handling](reference/exit-status-and-error-handling.md): `$?`, `set -euo pipefail` के flags और असली अपवाद, और पक्की सफ़ाई के लिए `trap`
- [Portability](reference/portability.md): POSIX `sh` बनाम bash-only features, shebang की ईमानदारी का नियम, और कब यह trade-off फ़ायदेमंद है
- [awk, sed, और कब रुकना है यह जानना](reference/awk-sed-and-when-to-stop.md): tool को काम के आकार से मिलाना, और वे ठोस संकेत कि script shell से बड़ी हो गई है

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
