---
title: Containers
description: "किसी service को container image के रूप में package करें और उसे अपने हाथ में लें: kernel primitives, Dockerfiles, एक container को चलाना, सुरक्षित करना और debug करना"
type: topic
---

# सीखना: Containers

किसी भी service को container image के रूप में package करें और एक host पर उसके साथ जो होता है उसकी ज़िम्मेदारी लें: जानें कि container चलते समय kernel क्या कर रहा है, ऐसा Dockerfile लिखें जो छोटी, reproducible image build करे, उसे ऐसे चलाएँ कि वह साफ़ ढंग से बंद हो और अपनी सीमाओं में रहे, उसे hardened बनाएँ, और जब वह शुरू न हो तो debug करें। अंत में किसी और के Dockerfile और image की समीक्षा हर चुनाव की क़ीमत का नाम लेकर कर सकें।

**नवीनतम पाठ:** [24. जब आम जवाब ग़लत हो](lessons/0024-when-the-usual-answer-is-wrong.md)

## सफलता कैसी दिखती है

- समझाएँ कि kernel की भाषा में container क्या है (namespaces, cgroups और परतों वाला root filesystem) और वह virtual machine से कैसे अलग है।
- Image को पढ़ें: उसका manifest, config और layers, tag और digest का फ़र्क़, और ठीक वही image pull करें जिसे परखा गया था।
- ऐसा Dockerfile लिखें जो multi-stage build का इस्तेमाल करके छोटी, cache के अनुकूल और reproducible image build करे।
- ऐसा container चलाएँ जो signal मिलने पर साफ़ ढंग से बंद हो, अपनी health report करे, और memory और CPU की उन सीमाओं में रहे जिनका सम्मान उसके भीतर का runtime करता है।
- एक host पर containers को जोड़ें: networking, published ports, state के लिए volumes, और local development के लिए Compose।
- Image को hardened बनाएँ: non-root user, न्यूनतम privileges, minimal base, triage किया गया vulnerability scan, layers से बाहर रखे गए secrets, और सत्यापित करने के लिए signature और provenance।
- ऐसे container को debug करें जो शुरू न हो या ग़लत व्यवहार करे, उसके exit code से लेकर उसके namespaces के भीतर तक, ऐसे container समेत जिसमें shell न हो।
- किसी और के Dockerfile और image की समीक्षा करें, base-image बदलाव को उस पर निर्भर services तक पहुँचाएँ, और बताएँ कि कब आम जवाब ग़लत है।

## सीमाएँ

- Linux command line पर सहजता और किसी भाषा में service build करके चलाने का अनुभव माना गया है। Containers का कोई पूर्व ज्ञान नहीं माना गया है।
- BuildKit के साथ Docker CLI का इस्तेमाल होता है, क्योंकि ज़्यादातर documentation और ज़्यादातर teams यही इस्तेमाल करती हैं। जहाँ कोई व्यवहार Docker का नहीं बल्कि OCI specifications का है, वहाँ पाठ यह बताता है, और वही commands ज़्यादातर Podman में भी काम करती हैं।
- चरण 1 के अभ्यासों के लिए root वाला Linux shell चाहिए, जैसे Linux machine या virtual machine। Docker Desktop चलाने वाले laptop पर containers ख़ुद उस Linux virtual machine के भीतर चलते हैं जिसे Docker Desktop संभालता है।

## दायरे से बाहर

- किसी एक भाषा के लिए चलने योग्य artifact build करना। यह भाषा वाले tracks का हिस्सा है और यह track उनके output को image में रखता है: static binaries के लिए [Go: Toolchain Commands](../../programming/golang/reference/toolchain-commands.md), चलने योग्य artifacts और `jlink` के लिए [Java: Testing और Build](../../programming/java/reference/testing-and-build.md) और [Module System](../../programming/java/reference/the-module-system.md), [C#: Service को Ship करना](../../programming/csharp/reference/shipping-the-service.md), और wheels के लिए [Python: Project और Packaging](../../programming/python/reference/project-and-packaging.md)।
- Cluster के पार containers का orchestration: scheduling, services, rollouts, cluster feature के रूप में probes। यह [Kubernetes track](../kubernetes/README.md) है। यह track एक host पर एक container, या कुछ containers, पर रुक जाता है।
- Pipeline में images build और publish करना। यह [CI/CD track](../ci-cd/README.md) है, जिसकी [Artifacts और Versioning](../ci-cd/reference/artifacts-and-versioning.md) sheet tagging और digest से publish करना कवर करती है। यह track images हाथ से build करता है ताकि पहले यह समझ आए कि pipeline क्या automate करती है।
- Windows containers, और container runtime लिखना।

## पूरी रूपरेखा

आठ चरण, container क्या है से लेकर किसी और की image की समीक्षा करने के विवेक तक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Container क्या है | 0001 से 0003 | Process के रूप में container, namespaces, cgroups, virtual machine से फ़र्क़ | Container का isolation हाथ से बना सकें और बता सकें कि हर हिस्सा क्या छिपाता या सीमित करता है |
| 2. Images | 0004 से 0006 | Manifest, config और layers, overlayfs, runtime stack और lifecycle, registries, tags और digests | Image पढ़ सकें और ठीक वही pull कर सकें जिसे परखा गया था |
| 3. Images build करना | 0007 से 0010 | Dockerfile instructions और build context, build cache, multi-stage builds और base images, reproducibility | ऐसा Dockerfile लिख सकें जो छोटी, cache के अनुकूल, reproducible image build करे |
| 4. एक container चलाना | 0011 से 0013 | PID 1 और signals, health checks और restart policies, memory और CPU सीमाएँ | ऐसा container चला सकें जो साफ़ ढंग से रुके, अपनी health report करे और अपनी सीमाओं का सम्मान करे |
| 5. Networking, storage और Compose | 0014 से 0016 | Bridge networks और published ports, volumes और bind mounts, local development के लिए Compose | एक host पर service और उसकी dependencies को साथ चला सकें, ऐसी state के साथ जो बची रहे |
| 6. Security | 0017 से 0019 | Non-root, capabilities और privilege, minimal bases और scanning, build secrets, signing और provenance | Image को hardened बना सकें और सत्यापित कर सकें कि वह कहाँ से आई |
| 7. Debugging | 0020 से 0021 | Exit codes, logs और inspect, entrypoint को override करना, container के namespaces में शामिल होना | पता लगा सकें कि container शुरू क्यों नहीं होता या ग़लत व्यवहार क्यों करता है, shell के बिना भी |
| 8. विवेक | 0022 से 0024 | Dockerfile की समीक्षा, ऐसी base image बदलना जिस पर दूसरे निर्भर हैं, कब आम जवाब ग़लत है, specification से उसे तय करना | Image पर निर्णय लेने और उसे किसी और को समझाने के लिए भरोसेमंद |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-a-container-is-a-process.md) | Container एक Process है | Container एक साधारण Linux process है जिसे kernel machine का सीमित दृश्य दिखाता है, कोई छोटी virtual machine नहीं |
| [0002](lessons/0002-namespaces.md) | Namespaces | हर namespace type एक तरह के global resource को छिपाता है, और unshare container का दृश्य एक-एक namespace करके बनाता है |
| [0003](lessons/0003-cgroups.md) | Cgroups | Control groups किसी process tree की memory, CPU और PIDs को सीमित करते और उनका हिसाब रखते हैं, और सीमा पर पहुँचने पर kernel क्या करता है |
| [0004](lessons/0004-images-and-layers.md) | Images और Layers | OCI image एक manifest, एक config और layer tarballs का ढेर है जिन्हें overlayfs एक root filesystem में मिला देता है |
| [0005](lessons/0005-from-image-to-running-container.md) | Image से चलते Container तक | Image और process के बीच docker run क्या करता है: runtime stack, writable layer और lifecycle |
| [0006](lessons/0006-registries-tags-and-digests.md) | Registries, Tags और Digests | Tag एक खिसकने वाला नाम है और digest सामग्री का hash, इसलिए ठीक वही चलाने के लिए जिसे परखा गया था, digest से pull करें |
| [0007](lessons/0007-your-first-dockerfile.md) | आपका पहला Dockerfile | Image build करने वाली instructions, build context, और .dockerignore उसमें से क्या बाहर रखता है |
| [0008](lessons/0008-the-build-cache.md) | Build Cache | Cached layer कब दोबारा इस्तेमाल होती है, उसे और उसके बाद की हर layer को क्या अमान्य करता है, और instructions का क्रम rebuild का समय कैसे तय करता है |
| [0009](lessons/0009-multi-stage-builds.md) | Multi-Stage Builds | एक stage में build करें, सिर्फ़ artifact को minimal अंतिम stage में copy करें, और हर base image चुनाव की क़ीमत क्या है |
| [0010](lessons/0010-reproducible-builds.md) | Reproducible Builds | एक ही Dockerfile के दो builds को क्या अलग बनाता है, और bases, packages और timestamps को pin करना ताकि वे अलग न हों |
| [0011](lessons/0011-pid-1-and-signals.md) | PID 1 और Signals | जब container का process PID 1 हो या shell में लिपटा हो तो वह SIGTERM को अनदेखा क्यों करता है, और शालीनता से कैसे बंद हों |
| [0012](lessons/0012-health-checks-and-restart-policies.md) | Health Checks और Restart Policies | Report करें कि भीतर का process असल में काम कर रहा है या नहीं, और तय करें कि उसके रुकने पर runtime क्या करे |
| [0013](lessons/0013-resource-limits-in-practice.md) | व्यवहार में Resource Limits | Memory और CPU सीमाएँ सेट करें, OOM kill और CPU throttling को पढ़ें, और जाँचें कि भीतर का runtime सीमा देखता है |
| [0014](lessons/0014-container-networking.md) | Container Networking | Network namespaces, veth pairs और bridge containers को जोड़ते हैं, और port publish करना host पर एक NAT rule जोड़ता है |
| [0015](lessons/0015-volumes-and-state.md) | Volumes और State | Named volumes, bind mounts और tmpfs में data container से ज़्यादा कहाँ टिकता है, और host और container के बीच file-ownership का जाल |
| [0016](lessons/0016-compose-for-local-development.md) | Local Development के लिए Compose | Service और उसकी dependencies को एक Compose file में बताएँ, और dependency के शुरू होने के बजाय उसके healthy होने का इंतज़ार करें |
| [0017](lessons/0017-least-privilege.md) | Least Privilege | Non-root user के रूप में चलाएँ, capabilities हटाएँ, root filesystem को read-only रखें, और जानें कि privileged mode और Docker socket क्या सौंप देते हैं |
| [0018](lessons/0018-minimal-bases-and-scanning.md) | Minimal Bases और Scanning | Image में जो है उसे घटाएँ, vulnerability scan पढ़ें, और शून्य गिनती के पीछे भागने के बजाय उसके findings का triage करें |
| [0019](lessons/0019-secrets-signing-and-provenance.md) | Secrets, Signing और Provenance | Secrets को layers से बाहर रखें, image को digest से sign करें, और चलाने से पहले सत्यापित करें कि वह कहाँ build हुई |
| [0020](lessons/0020-a-container-that-will-not-start.md) | ऐसा Container जो शुरू न हो | Exit code, logs और inspect output पढ़ें, फिर यह पता लगाने के लिए entrypoint override करें कि वह क्यों रुका |
| [0021](lessons/0021-debugging-a-running-container.md) | चलते Container को Debug करना | Debug container से या host से उसके namespaces में शामिल होकर ऐसे container के भीतर जाएँ जिसमें shell नहीं है |
| [0022](lessons/0022-reviewing-a-dockerfile.md) | Dockerfile की समीक्षा | किसी और के Dockerfile और image की समीक्षा, हर चुनाव की size, rebuild समय, security और reliability में क़ीमत का नाम लेकर |
| [0023](lessons/0023-changing-a-base-image-others-depend-on.md) | ऐसी Base Image बदलना जिस पर दूसरे निर्भर हैं | Tags, digests, rebuilds और deprecation का इस्तेमाल करके साझा base image को उस पर बनी services को तोड़े बिना आगे बढ़ाएँ |
| [0024](lessons/0024-when-the-usual-answer-is-wrong.md) | जब आम जवाब ग़लत हो | पहचानें कि कब Alpine, distroless, pinned digest या container ख़ुद ही ग़लत निर्णय है, और specification से उसे तय करें |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत, हर एक के साथ टिप्पणी कि वह क्या कवर करता है
- [Container Primitives](reference/container-primitives.md): namespaces, cgroups, image layout और tags बनाम digests, चरण 1 और 2 से
- [Dockerfile](reference/dockerfile.md): instructions, cache के नियम, multi-stage patterns, base images और reproducibility, चरण 3 से
- [Containers चलाना](reference/running-containers.md): signals, health checks, सीमाएँ, networking, volumes और Compose, चरण 4 और 5 से
- [Container Security](reference/container-security.md): privileges, minimal bases, scan triage, build secrets, signing और provenance, चरण 6 से
- [Containers को Debug करना](reference/debugging-containers.md): exit codes, क्रम से चलाने वाली commands, और shell के बिना container के भीतर कैसे जाएँ, चरण 7 से
- [Dockerfile समीक्षा Checklist](reference/dockerfile-review-checklist.md): किसी और के Dockerfile और image से पूछे जाने वाले सवाल, और कब आम जवाब ग़लत है, चरण 8 से

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
