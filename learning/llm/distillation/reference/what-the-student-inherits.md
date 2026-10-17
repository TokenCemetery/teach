---
title: What the Student Inherits
description: Fidelity, the imitation gap, the capacity gap and unintended traits, with each source's setting and numbers
type: reference
---

# What the Student Inherits: Fidelity, the Imitation Gap, the Capacity Gap and Hidden Traits

Stage 6 compressed for lookup. [Lesson 17](../lessons/0017-fidelity-and-generalization.md) covers fidelity against generalization, [lesson 18](../lessons/0018-the-imitation-gap.md) the imitation gap, and [lesson 19](../lessons/0019-capacity-gap-and-hidden-traits.md) the capacity gap and hidden traits.

## Four ways a student can differ from its teacher

| Gap | What differs | Source | Setting |
|---|---|---|---|
| Fidelity | Predictions on the same inputs, even when accuracy is similar | Stanton et al., 2021 | Image classification, with MNIST, CIFAR-100, ImageNet and IMDB sentiment in the appendix |
| Imitation | Style copied fast, capability not | Gudibande et al., 2023 | LLaMA and GPT-2 students imitating ChatGPT |
| Capacity | A very large teacher can give a worse student | Mirzadeh et al., 2019, and Cho and Hariharan, 2019 | CNNs and ResNets on CIFAR and ImageNet |
| Hidden traits | A trait passes through data that does not mention it | Cloud et al., 2025 | GPT-4.1 family and Qwen2.5-7B, plus a small MNIST case |

Only two of the four were tested on language models, and none of the capacity-gap evidence here is from LLMs.

## Measuring fidelity

| Metric | Definition | Needs |
|---|---|---|
| Top-1 agreement | Fraction of inputs where student and teacher pick the same top label | Teacher's predictions |
| Predictive KL | Mean KL(teacher, student) over inputs | Teacher's full distribution |
| Control | A second student distilled the same way from an independent teacher | A second distillation run |

Accuracy does not bound agreement tightly. With teacher accuracy 93% and student accuracy 91%, agreement lies between 84% and 98%.

## Stanton et al. in numbers

| Observation | Number or direction |
|---|---|
| LeNet-5 on MNIST with enough data | Over 99% top-1 test agreement |
| ResNet-56 self-distillation on CIFAR-100, largest set | Test agreement below 80% |
| Same, with 50k GAN images added, agreement on the distillation data itself | 95% |
| Same, with combined heavy augmentation, train agreement in self-distillation | About 60% |
| ResNet-20 self-distillation, SGD train agreement at 300 epochs and at 5,000 epochs | 78.95% and 83.3% |
| Self-distillation, more data | Fidelity up, test accuracy down |
| 3-ensemble teacher, more data | Fidelity and accuracy both up |

Their explanation is optimization: the student does not match the teacher even on the data it trains on. More distillation data helps identification of the teacher's function and makes optimization harder.

## Gudibande et al. in numbers

| Observation | Number |
|---|---|
| Crowd ratings of imitation outputs as equal or better than ChatGPT | About 70% |
| Natural Questions, LLaMA 7B: base, broad imitation, local imitation, ChatGPT | 17, 10, 22, 31 |
| Natural Questions, LLaMA 13B: base, broad imitation, local imitation, ChatGPT | 20, 15, 27, 31 |
| Outputs in an authoritative tone: base LLaMA against imitation models | 57% against 98% to 99% |

Their claim: with current methods the gap closes only with an unwieldy amount of imitation data or a more capable base model, and a better base model helped more than more imitation data in their experiments. Local imitation of one task worked much better than broad imitation. Imitation models also became less toxic, learning to abstain like the teacher.

## Capacity gap evidence

| Source | Finding | Remedy tried |
|---|---|---|
| Mirzadeh et al. | A 2-layer student's accuracy rose then fell as teachers grew from 4 to 10 layers | Teacher assistant. Gain over standard distillation 0.33 to 0.41 points on ResNet, 0.94 points on the plain CNN with CIFAR-10 |
| Cho and Hariharan | ResNet18 on ImageNet: scratch 30.24% error, 30.57%, 30.79% and 30.95% with ResNet18, 34 and 50 teachers | Early-stopped distillation gave 29.01%, 29.16% and 29.35%. Early-stopped teachers helped on CIFAR-10. Chaining through a medium model did not help |
| Gu et al. (MiniLLM) | GPT-2 125M student improved with teachers of 340M, 760M and 1.5B | No gap seen over that range, one family |

The two vision papers disagree on whether an intermediate model helps. Test on your own pair.

## Hidden traits, Cloud et al.

| Item | Detail |
|---|---|
| Setup | A teacher with a trait generates unrelated data, the data is filtered, a student from the same base is fine-tuned on it |
| Owl preference | About 12% before, over 60% after, from numbers only |
| Misalignment from numbers | Almost 10% misaligned responses, against 0% for the base and under 1% for controls |
| Misalignment from filtered chain of thought | About 0% to 8%, controls under 1% |
| Detection | Prompted classifiers and in-context learning did not reliably detect the trait |
| Condition | Shared base model. GPT-4.1 nano to Qwen2.5 did not transmit. GPT-4o and GPT-4.1 did, likely a shared initialization |
| Open limits | Artificial tasks, and which traits transmit and when is unknown |

## Symptom, likely cause, check

| Symptom | Likely cause | Check |
|---|---|---|
| Student matches teacher on accuracy but outputs differ | Low fidelity | Top-1 agreement and predictive KL on held-out inputs, with an independent-teacher control |
| Crowd ratings or judge scores high, targeted benchmarks flat | Style copied, capability not | Benchmarks on tasks the data barely covers, against the base model |
| Student worse than a smaller teacher's student | Capacity gap | Direct, one intermediate model, early-stopped teacher, against a scratch baseline |
| Unwanted behaviour appears though the data is clean | Hidden trait from a shared base | Evaluate the student for the behaviour directly, and consider a different base |
| Student refuses like its teacher | Refusal behaviour transfers with style | Compare refusal rates with the teacher on a fixed prompt set |

## What none of this covers

- No source read here shows that a student copies its teacher's factual errors.
- The capacity gap and the fidelity gap were measured on vision models, not on LLMs.
- Subliminal learning was shown on artificial tasks, and a different base blocking it was an observation in those experiments, not a guarantee.
