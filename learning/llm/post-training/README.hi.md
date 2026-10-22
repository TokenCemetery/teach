---
title: "LLM Post-Training"
description: "Base model को align करें: SFT, reward modeling, RLHF, DPO और GRPO, और यह जानना कि कौन-सा चुनना है"
type: topic
---

# सीखना: LLM Post-Training

pretrained base model को aligned, instruction-following assistant तक ले जा सकें: SFT, reward और preference objectives सही लिखें, किसी टीम के बजट और data के हिसाब से RLHF-PPO, DPO और GRPO में से चुनें, और उस चुनाव का बचाव करें, जिसमें यह भी शामिल है कि alignment tax में उसकी क्या क़ीमत लगी और वह reward hacking के सामने कहाँ खुला है।

**नवीनतम पाठ:** [20. किसी और की Alignment Recipe की समीक्षा](lessons/0020-reviewing-someone-elses-alignment-recipe.md)

## सफलता कैसी दिखती है

- ऐसा SFT training loop लिखें जो non-assistant tokens पर loss को mask करे, और समझाएँ कि उस mask के बिना train किए chat model में क्या टूटता है।
- Bradley-Terry loss से preference pairs पर reward model train करें, और उसके विरुद्ध train हुई policy की reward-hacked completion पहचानें।
- RLHF objective निकालें (reward में से reference model के विरुद्ध KL penalty घटाना), और बताएँ कि KL penalty ढीला करने पर policy का क्या होता है।
- उसी preference data से DPO का implicit reward निकालें जो RLHF इस्तेमाल करता है, और बताएँ कि RL loop हटाने से वह क्या छोड़ देता है।
- GRPO में group-relative advantage समझाएँ, और बताएँ कि verifiable reward (unit test, जाँचा हुआ गणित का उत्तर) से RL training किसे निशाना बना सकती है, यह कैसे बदल जाता है।
- किसी टीम के data, बजट और लक्षित व्यवहार को देखकर अकेला SFT, DPO, RLHF-PPO और GRPO में से चुनें, और जिसे नकारा उसके सामने चुनाव का बचाव करें।
- Aligned model के evaluation नतीजे पढ़ें और असली क्षमता-वृद्धि को reward hacking या judge bias की उपज से अलग करें।

## सीमाएँ

- Algorithm-first, पेपरों का सर्वेक्षण नहीं। हर चरण एक training objective को उसके loss function से बाहर की ओर सिखाता है, यानी क्या maximize हो रहा है और gradient क्या करता है, पेपरों की सूची का सार देने के बजाय; पेपर हर चरण के मुख्य स्रोत के रूप में उसे टिकाते हैं।
- छोटे पैमाने का अभ्यास: labs किसी छोटे open model पर SFT और DPO चलाते हैं, वही पैमाने का अनुशासन जो `llm/finetuning` इस्तेमाल करता है, और वहाँ से यह तर्क करते हैं कि जिन frontier पेपरों का हवाला दिया गया है वे क्या रिपोर्ट करते हैं।
- मानकर चला गया है कि आपने `llm/transformers` (cross-entropy loss, backward pass, AdamW) पढ़ा है और `llm/finetuning` के adapter mechanics से परिचित हैं, क्योंकि यह track parameter efficiency को दोबारा निकालने के बजाय उन्हें दोबारा इस्तेमाल करता है।
- कोई पाठ frontier पैमाने पर पूरा RLHF pipeline शुरू से अंत तक train नहीं करता; PPO की लागत छोटे पैमाने पर दिखाई जाती है और फिर उस पैमाने पर तर्क से समझी जाती है जो हवाला दिए गए पेपर रिपोर्ट करते हैं।

## दायरे से बाहर

- Parameter-efficient mechanics (LoRA का rank और alpha, QLoRA, DoRA, target modules): [`llm/finetuning`](../../llm/finetuning/) देखें। यह track training objective सँभालता है; उसे कम parameters पर कैसे लगाया जाता है, यह `llm/finetuning` सँभालता है।
- Cross-entropy loss, backward pass और AdamW: [`llm/transformers`](../../llm/transformers/) देखें। यहाँ माने हुए हैं, दोबारा सिखाए नहीं जाते।
- LLM-as-judge की mechanics और human evaluation की पद्धति: [`llm/evals`](../../llm/evals/) देखें। यहाँ सिर्फ़ उस एक क्षमता के रूप में ली गई है जो aligned model को चाहिए, यानी यह आँकना कि alignment training से फ़ायदा हुआ या नहीं, और उसे दोहराने के बजाय उसकी ओर link किया गया है।
- Reasoning model को prompt करना, या उसके इर्द-गिर्द agent बनाना: [`llm/agents`](../../llm/agents/) (पाठ 0017) देखें। यह track बताता है कि reasoning का व्यवहार RL training से कैसे पैदा होता है, बाहर से उसे कैसे इस्तेमाल करें यह नहीं।
- Random initialization से model को train करना: [`llm/pretraining`](../../llm/pretraining/) देखें।
- सामान्य रूप से distillation, reasoning-model वाले मामले से आगे: [`llm/distillation`](../../llm/distillation/) देखें। यहाँ का पाठ 0014 reasoning-model का मामला बना रहता है और सामान्य विधि के लिए वहाँ link करता है।
- Prompting से बाहर से instruction-following और reasoning का इस्तेमाल: [`llm/prompting`](../../llm/prompting/) देखें। यह track बताता है कि वे व्यवहार model में कैसे train किए जाते हैं।

## पूरी रूपरेखा

दस चरण, बिना किसी पूर्व ज्ञान से वरिष्ठ स्तर के विवेक तक। पाठों की सूची नहीं: एक चरण में कई पाठ लगते हैं, और सीमाएँ लचीली हैं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
| --- | --- | --- | --- |
| 1. Post-training से क्या मिलता है | 0001 से 0001 | Base बनाम instruct/chat model, SFT/RLHF/DPO/GRPO का नक़्शा | किसी दिए aligned model के व्यवहार को उस post-training चरण के सामने रख सकें जिसने उसे पैदा किया |
| 2. SFT | 0002 से 0003 | Instruction datasets, chat templates, non-assistant tokens पर loss masking | सही loss masking वाला SFT loop लिख सकें और बता सकें कि उसके बिना क्या टूटता है |
| 3. Reward modeling | 0004 से 0005 | Preference data का संग्रह, Bradley-Terry loss, reward hacking | Reward model train कर सकें और उसके विरुद्ध reward-hacked completion पहचान सकें |
| 4. PPO के ज़रिए RLHF | 0006 से 0008 | RL objective, reference model के विरुद्ध KL penalty, PPO महँगा और अस्थिर क्यों है | RLHF objective निकाल सकें और बता सकें कि KL penalty ढीला करने से policy का क्या होता है |
| 5. Direct Preference Optimization | 0009 से 0010 | DPO का implicit reward, वह PPO की तुलना में क्या छोड़ता है और यह आम तौर पर ठीक क्यों है | DPO का implicit reward निकाल सकें और बता सकें कि वह PPO की तुलना में क्या छोड़ देता है |
| 6. GRPO और verifiable rewards के साथ RL | 0011 से 0012 | Group-relative advantage, यह गणित और code के लिए क्यों फ़िट बैठता है | Group-relative advantage समझा सकें और बता सकें कि verifiable reward से RL किसे निशाना बना सकता है, यह कैसे बदलता है |
| 7. Reasoning models | 0013 से 0014 | Chain-of-thought RL, DeepSeek-R1 ने क्या बदला, reasoning model को distil करके छोटा करना | बता सकें कि reasoning model का व्यवहार कैसे पैदा हुआ, सिर्फ़ यह नहीं कि उसे कैसे prompt करें |
| 8. Safety और refusal tuning | 0015 से 0016 | Red-teaming data, Constitutional AI, RLAIF | किसी दी गई safety-tuning pipeline में बता सकें कि feedback कहाँ से आया (इंसान या AI) और उसमें क्या लेन-देन है |
| 9. Aligned model का मूल्यांकन | 0017 से 0018 | Alignment tax, reward hacking की पहचान, `llm/evals` से जोड़ना | असली क्षमता-वृद्धि को reward-hacking या judge-bias की उपज से अलग कर सकें |
| 10. विवेक | 0019 से 0020 | किसी बजट के लिए DPO बनाम PPO बनाम GRPO, अकेला SFT कब काफ़ी है, किसी और की alignment recipe की समीक्षा | फ़ैसला लेने और उसे किसी और को समझाने के लिए भरोसेमंद हों |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-what-post-training-buys.md) | Post-Training से क्या मिलता है | 100 गुना छोटे aligned model ने कच्चे base model को हरा दिया, उस काम में जो users को असल में चाहिए था |
| [0002](lessons/0002-instruction-data-and-the-chat-template.md) | Instruction Data और Chat Template | एक special token बताता है कि prompt कहाँ ख़त्म होता है और उत्तर कहाँ शुरू, और यह सीमा training और serving के समय एक जैसी होनी चाहिए |
| [0003](lessons/0003-loss-masking-on-non-assistant-tokens.md) | गैर-Assistant Tokens पर Loss Masking | Prompt पर loss को शून्य करें, वरना gradient signal उस text का अनुमान लगाना सिखाने में ख़र्च होता है जिसे model ने generate नहीं किया |
| [0004](lessons/0004-training-a-reward-model-the-bradley-terry-loss.md) | Reward Model को Train करना: Bradley-Terry Loss | Reward model training में कभी कोई निरपेक्ष score नहीं देखता, सिर्फ़ यह कि दो completions में से इंसान को कौन-सी ज़्यादा पसंद आई |
| [0005](lessons/0005-reward-hacking.md) | Reward Hacking | एक policy ने लगभग हर चीज़ पर "I can't answer that" कहना सीख लिया, क्योंकि इससे बिना सचमुच helpful या harmless हुए अच्छा score मिलता था |
| [0006](lessons/0006-the-rlhf-objective-reward-minus-a-kl-penalty.md) | RLHF Objective: Reward में से KL Penalty घटाना | एक term reward model का score बटोरता है; दूसरा term वह पट्टा है जो policy को उसे लेकर भाग जाने से रोकता है |
| [0007](lessons/0007-ppo-why-the-update-gets-clipped.md) | PPO: Update को Clip क्यों किया जाता है | Sample किए data के एक batch पर बड़ी जीत बड़े क़दम का भरोसेमंद सबूत नहीं है; PPO उस पर पूरा यक़ीन करने से इनकार करता है |
| [0008](lessons/0008-why-ppo-is-expensive-and-unstable.md) | PPO महँगा और अस्थिर क्यों है | एक नहीं, चार models को एक साथ memory में समाना पड़ता है, और जो दो सबसे बुरी तरह scale होते हैं वे ठीक वही हैं जो RLHF जोड़ता है |
| [0009](lessons/0009-dpos-implicit-reward-why-the-partition-function-cancels.md) | DPO का Implicit Reward: Partition Function क्यों कट जाता है | Reward और उसकी optimal policy के बीच एक अगम्य normalizing term खड़ा है, जब तक कि दो rewards का अंतर उसे ग़ायब नहीं कर देता |
| [0010](lessons/0010-the-dpo-loss-and-what-it-drops-relative-to-ppo.md) | DPO Loss, और PPO की तुलना में वह क्या छोड़ देता है | एक loss, दो models, कोई sampling loop नहीं, और वही beta जो KL penalty इस्तेमाल करता |
| [0011](lessons/0011-grpo-group-relative-advantage-instead-of-a-value-function.md) | GRPO: Value Function की जगह Group-Relative Advantage | एक ही सवाल के कई उत्तर sample करें, और group के rewards के अपने फैलाव को बताने दें कि कौन-से बेहतर थे |
| [0012](lessons/0012-verifiable-rewards-when-a-checker-replaces-the-reward-model.md) | Verifiable Rewards: जब Checker, Reward Model की जगह ले लेता है | Train किया हुआ reward model इस बात का अंदाज़ा है कि इंसान को क्या पसंद आएगा; unit test या मेल खाता उत्तर अंदाज़ा बिल्कुल नहीं है |
| [0013](lessons/0013-chain-of-thought-rl-what-deepseek-r1-zero-did-with-rule-based-rewards.md) | Chain-of-Thought RL: DeepSeek-R1-Zero ने Rule-Based Rewards के साथ क्या किया | न सीखा हुआ reward model, न पहले SFT का कोई चरण, फिर भी लंबी reasoning उभर आई क्योंकि उससे ज़्यादा उत्तर सही होते रहे |
| [0014](lessons/0014-distilling-a-reasoning-model-down.md) | Reasoning Model को Distil करके छोटा करना | 32B model को सीधे RL से train करना, उसे बड़े model के अपने reasoning traces पर fine-tune करने से हार गया |
| [0015](lessons/0015-constitutional-ai-feedback-from-a-model-not-a-human.md) | Constitutional AI: Feedback इंसान से नहीं, Model से | नुक़सान के लिए इंसानी labels शून्य, उनकी जगह लिखे हुए सिद्धांतों की सूची, और एक assistant जो टालने के बजाय अपनी आपत्तियाँ समझाता है |
| [0016](lessons/0016-rlaif-how-well-ai-feedback-actually-matches-human-feedback.md) | RLAIF: AI Feedback असल में Human Feedback से कितना मेल खाता है | अपने ही आकार का model, अपने ही outputs को परखकर, फिर भी सादे supervised fine-tuning से बेहतर निकला |
| [0017](lessons/0017-measuring-the-alignment-tax.md) | Alignment Tax को मापना | Tax हर जगह एक साथ नहीं दिखता, और एक axis पर तो गिरावट की जगह सुधार मापा गया |
| [0018](lessons/0018-reward-hacking-after-the-fact.md) | बाद में Reward Hacking की जाँच | Held-out reward model training के दौरान drift पकड़ सकता है; तैयार model के लिए अलग तरह की जाँच चाहिए |
| [0019](lessons/0019-choosing-between-sft-dpo-ppo-and-grpo.md) | SFT, DPO, PPO और GRPO में से चुनना | हर तरीक़ा अपनी जोड़ी गई लागत तब ही सही ठहराता है जब उससे पहले वाला सस्ता तरीक़ा लक्षित व्यवहार को सचमुच व्यक्त न कर पाए |
| [0020](lessons/0020-reviewing-someone-elses-alignment-recipe.md) | किसी और की Alignment Recipe की समीक्षा | Pipeline को इस track के हर चरण से क्रम से गुज़ारें, और विवादित दावे का निपटारा आत्मविश्वास भरे दोहराव से नहीं, स्रोत से करें |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके मुख्य स्रोत तक खंगालना ठीक रहेगा।
