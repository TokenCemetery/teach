---
title: "संसाधन"
description: "LLM post-training के लिए भरोसेमंद स्रोत"
type: resources
---

# LLM Post-Training संसाधन

## ज्ञान

- [पेपर: "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
  InstructGPT पेपर। वह SFT, reward-model, PPO pipeline तय करता है जिसे तब से ज़्यादातर RLHF काम ने अपनाया है, और alignment tax को केवल pretrained model के सामने मापता है। इस्तेमाल: चरण 1, 2, 3 के लिए, और चरण 9 के alignment-tax वाले ढाँचे के लिए।
- [पेपर: "Proximal Policy Optimization Algorithms", Schulman et al., 2017](https://arxiv.org/abs/1707.06347)
  PPO को सामान्य reinforcement-learning algorithm के रूप में पेश करता है, language models से स्वतंत्र। इस्तेमाल: चरण 4 के मूल algorithm के लिए, उसके language-model वाले इस्तेमाल से पहले पढ़ें।
- [पेपर: "Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback", Bai et al., 2022](https://arxiv.org/abs/2204.05862)
  उसी SFT-से-RLHF recipe का Anthropic का production पैमाने का ब्योरा, जिसमें यह भी है कि reward model के विरुद्ध reward hacking और over-optimization व्यवहार में कहाँ दिखे। इस्तेमाल: चरण 3 की reward-hacking सामग्री और चरण 4 में असल में क्या ग़लत होता है, इसके ब्योरे के लिए।
- [पेपर: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
  Policy और reference model से तय होने वाला closed-form reward निकालता है, जो अलग reward model और RL loop की जगह preference pairs पर एक supervised-style loss रख देता है। इस्तेमाल: चरण 5 की केंद्रीय derivation के लिए।
- [पेपर: "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
  GRPO पेश करता है, जो PPO के सीखे हुए value function की जगह हर prompt की कई sample की गई completions से निकला group-relative baseline रखता है। इस्तेमाल: चरण 6 के केंद्रीय algorithm के लिए।
- [पेपर: "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning", DeepSeek-AI, 2025](https://arxiv.org/abs/2501.12948)
  लंबी chain-of-thought reasoning को मुख्य रूप से verifiable rewards के विरुद्ध RL से train करता है, और नतीजे के व्यवहार को छोटे models में distil करने का वर्णन करता है। इस्तेमाल: चरण 7 के मुख्य स्रोत के रूप में।
- [पेपर: "Constitutional AI: Harmlessness from AI Feedback", Bai et al., 2022](https://arxiv.org/abs/2212.08073)
  इंसानों के labelled harmlessness preferences की जगह ऐसा model रखता है जो लिखे हुए सिद्धांतों के सेट के विरुद्ध अपने ही outputs की आलोचना करके उन्हें सुधारता है। इस्तेमाल: चरण 8 में उस feedback के केंद्रीय मामले के लिए जो इंसान के बजाय model ने बनाया।
- [पेपर: "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback", Lee et al., 2023](https://arxiv.org/abs/2309.00267)
  उन्हीं tasks पर RLAIF और RLHF की सीधी, नियंत्रित तुलना, जो बताती है कि AI feedback कहाँ human feedback से मेल खाता है और कहाँ नहीं। इस्तेमाल: चरण 8 के लिए, Constitutional AI की विधि के अनुभवजन्य पूरक के रूप में।
- [पेपर: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
  Open-model पैमाने पर प्रकाशित एक RLHF recipe, जिसमें reward model training का ब्योरा और कई दौरों में चलने वाली iterative RLHF प्रक्रिया शामिल है। इस्तेमाल: चरण 3 और 4 को एक पूरी, दोहराई जा सकने वाली recipe से मिलाकर जाँचने के लिए।
- [दस्तावेज़: "TRL - Transformer Reinforcement Learning", Hugging Face](https://huggingface.co/docs/trl/index)
  वह library जो इस track के SFT और DPO labs असल में चलाते हैं, हर trainer के काम करते हुए configuration के साथ। इस्तेमाल: चरण 2, 4 और 5 के हाथ से किए जाने वाले अभ्यास के लिए।

## कमियाँ

- Preference-data की गुणवत्ता पर अभी कोई मुख्य स्रोत नहीं: annotators की असहमति, labeling के निर्देश, और preference-data संग्रह के चुनाव train हुए reward model को कैसे झुकाते हैं। चरण 3 की data-गुणवत्ता वाली सामग्री को पूरी तरह टिकाने से पहले यह चाहिए।
- InstructGPT की अपनी रिपोर्ट से आगे alignment-tax का मापन कम है; कोई नया, model-agnostic विवेचन चरण 9 को मज़बूत करेगा।
- किसी एक टीम के infrastructure से DPO बनाम PPO बनाम GRPO की पूरी लागत-तुलना का अभी कोई production ब्योरा नहीं; चरण 10 के विवेक वाले पाठ को यह तुलना अलग-अलग पेपरों से जोड़नी पड़ती है, ऐसे एकल स्रोत से नहीं जिसने तुलना पहले ही कर दी हो।
