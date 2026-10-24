---
title: CI/CD
description: "हर बदलाव को pipeline से build, test और deliver करें और उसे अपने हाथ में लें: workflows, तेज़ feedback, artifacts, secrets, deployments, rollback और supply-chain security"
type: topic
---

# सीखना: CI/CD

किसी भी service को merge हुए बदलाव से लेकर production में चलने तक ऐसी pipeline से ले जाएँ जो आपकी ज़िम्मेदारी है: मिनटों में साबित करें कि हर बदलाव build होता है और उसके tests pass होते हैं, एक versioned artifact बनाएँ और उसी artifact को environments के बीच promote करें, pipeline को लंबे समय तक चलने वाली keys के बिना वह access दें जिसकी उसे ज़रूरत है, ऐसी रणनीति से deploy करें जो ख़राब release के नुक़सान को सीमित करे, और जब कोई ख़राब release निकल जाए तो roll back करें। अंत में किसी और की pipeline की समीक्षा यह बताकर कर सकें कि सबसे पहले क्या fail होगा, धीमा होगा या leak होगा, ऐसे workflow को बदल सकें जिस पर दूसरी teams निर्भर हैं, उनके merges तोड़े बिना, और बता सकें कि कब delivery का आम जवाब ग़लत है।

**नवीनतम पाठ:** [30. जब आम जवाब ग़लत हो](lessons/0030-when-the-usual-answer-is-wrong.md)

## सफलता कैसी दिखती है

- समझाएँ कि continuous integration, continuous delivery और continuous deployment हर एक क्या वादा करता है, और वादा निभाने के लिए team को क्या अभ्यास करना पड़ता है।
- Pipeline को code के रूप में लिखें: triggers और events, jobs, steps और runners, actions, expressions, contexts और outputs।
- ऐसे build और test stages चलाएँ जो सबसे सस्ती समस्या पर पहले fail हों, matrix पर, caching के साथ, flaky test पर भरोसा किए बिना, और इतने तेज़ कि लोग परिणाम का इंतज़ार करें।
- ऐसे artifacts बनाएँ जिनका version किसी commit तक trace हो, उन्हें एक बार build करें, और container image को build, publish करें और digest से refer करें।
- Pipeline को least privilege के साथ secrets और cloud access दें: सीमित `GITHUB_TOKEN` permissions, लंबे समय तक चलने वाली keys के बजाय OIDC, और untrusted input के लिए दोनों में से किसी तक पहुँचने का कोई रास्ता नहीं।
- Environments और approvals से deployments पर रोक लगाएँ, और एक artifact को staging से production तक promote करें।
- Rolling, blue-green और canary रणनीतियों से deploy करें, roll back या roll forward करें, deploy के इर्द-गिर्द database migrations का क्रम तय करें, और push deploy और GitOps में से चुनें।
- Supply chain को सुरक्षित करें: pipeline जो चलाती है उसे pin करें, और provenance और SBOMs बनाएँ और सत्यापित करें।
- Reusable workflows, composite actions और path filters से pipelines को repositories और monorepos के पार scale करें, और ऐसी pipeline को debug करें जो सिर्फ़ runner पर fail होती है।
- किसी और की pipeline की समीक्षा करें, साझा workflow या required check को उस पर निर्भर teams को तोड़े बिना बदलें, बताएँ कि कब आम जवाब ग़लत है, और विवादित व्यवहार को workflow syntax reference से तय करें।

## सीमाएँ

- Git, shell और किसी एक भाषा में project build और test करने में सहजता मानी गई है। CI/CD का कोई पूर्व ज्ञान नहीं माना गया है। पाठ 13 [containers track](../containers/README.md) या उसके बराबर ज्ञान मानता है, और पाठ 19 और 22 [Kubernetes track](../kubernetes/README.md) की बुनियादी बातें मानते हैं।
- Pipeline जो काम करती है वे सिखाए जाते हैं और GitHub Actions से किए जाते हैं, उसी तरह जैसे `programming/java` build lifecycle को Maven से सिखाता है। Jenkins और GitLab CI सिर्फ़ वहीं आते हैं जहाँ उनका model सचमुच अलग है।
- हर अभ्यास free GitHub account पर एक फेंक देने योग्य public repository में चलता है, जहाँ GitHub-hosted runners की कोई क़ीमत नहीं। Deployment अभ्यास job के भीतर बने kind cluster पर deploy करते हैं, इसलिए cloud account की ज़रूरत नहीं है। जहाँ कोई पाठ cloud provider पर निर्भर है, जैसे OIDC trust policy, वहाँ वह हिस्सा दिखाया जाता है जो अकेला GitHub दिखा सकता है और बाक़ी को वैकल्पिक बताया जाता है।

## दायरे से बाहर

- किसी एक भाषा का code build और test करना। Pipeline step जो commands चलाता है वे भाषा वाले tracks का हिस्सा हैं, जैसे [Java: Testing और Build](../../programming/java/reference/testing-and-build.md), [Go: Toolchain Commands](../../programming/golang/reference/toolchain-commands.md), [Python: Project और Packaging](../../programming/python/reference/project-and-packaging.md) और [C#: Testing और Build](../../programming/csharp/reference/testing-and-build.md)। यह track उन steps को pipeline में चलाता है।
- Dockerfile लिखना और image हाथ से build करना। यह [containers track](../containers/README.md) है, जिसकी [Dockerfile](../containers/reference/dockerfile.md) sheet वही है जिसे पाठ 13 pipeline में build करता है।
- Deliver होने के बाद workload चलाना: probes, cluster feature के रूप में rollouts, manifests की packaging। यह [Kubernetes track](../kubernetes/README.md) है, जिसकी [Packaging](../kubernetes/reference/packaging.md) sheet वे manifests कवर करती है जिन्हें deploy job लागू करता है। यह track बदलाव को उस तक पहुँचाता है, और GitOps सिर्फ़ उतना सिखाता है जितना उसे चुनने के लिए ज़रूरी है।
- ऐसा migration लिखना जो table को lock न करे। यह [SQL](../../programming/sql/README.md) है, जिसकी [Operating](../../programming/sql/reference/operating.md) sheet में migration safety तालिका है। यह track deploy के भीतर migrations का क्रम तय करता है।
- CI server install और administer करना, JavaScript या Docker container actions लिखना, और mobile app store release।

## पूरी रूपरेखा

दस चरण, CI और CD क्या वादा करते हैं से लेकर किसी और की pipeline की समीक्षा करने के विवेक तक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. CI और CD किसलिए हैं | 0001 से 0002 | वादों के रूप में integration, delivery और deployment, trunk-based काम, code के रूप में pipelines, Jenkins और GitLab के समकक्ष | बता सकें कि pipeline क्या गारंटी देती है और किसी भी workflow file को code की तरह पढ़ सकें |
| 2. Workflow की बनावट | 0003 से 0005 | Events और filters, jobs, steps, runners, `needs`, actions, expressions, contexts और outputs | ऐसा workflow लिख सकें जो इरादे के मुताबिक़ चले और jobs के बीच data पास करे |
| 3. तेज़, भरोसेमंद feedback | 0006 से 0010 | Stages का क्रम, service containers, matrices, caching, flaky tests, critical path, concurrency और timeouts | ऐसी pipeline चला सकें जिस पर लोग भरोसा करें और जिसका इंतज़ार करें |
| 4. Artifacts और versioning | 0011 से 0013 | Artifacts बनाम caches, build identity, एक बार build करना, image को digest से build और publish करना | एक trace होने योग्य artifact बना सकें और वही हर बाद के stage को सौंप सकें |
| 5. Secrets और भरोसा | 0014 से 0016 | Secrets, masking, `GITHUB_TOKEN` permissions, OIDC federation, script injection, `pull_request_target` | Pipeline को सिर्फ़ उतना access दे सकें जितना उसे चाहिए और untrusted input को उससे दूर रख सकें |
| 6. Environments और promotion | 0017 से 0018 | Environments, protection rules, environment secrets, हर environment के configuration के साथ एक artifact को promote करना | Production deploy पर रोक लगा सकें और वही promote कर सकें जिसे staging ने परखा |
| 7. Deploy और roll back करना | 0019 से 0022 | Recreate, rolling, blue-green और canary, rollback, roll forward और flags, expand और contract migrations, push deploys और GitOps | नुक़सान सीमित करने वाली रणनीति से deploy कर सकें और ख़राब release को पलट सकें |
| 8. Supply chain | 0023 से 0024 | Actions और dependencies को pin करना, Dependabot, SLSA provenance, artifact attestations, SBOMs | बता सकें कि pipeline ने क्या चलाया और साबित कर सकें कि artifact कहाँ से आया |
| 9. बड़े पैमाने पर pipelines | 0025 से 0027 | Reusable workflows, composite actions, monorepos में path filters और required checks, debug logging, runner के फ़र्क़ | Pipeline logic को teams के बीच साझा कर सकें और पता लगा सकें कि कोई run क्यों fail हुआ |
| 10. विवेक | 0028 से 0030 | Pipeline की समीक्षा, साझा workflow या required check बदलना, कब आम जवाब ग़लत है, workflow syntax reference से उसे तय करना | Pipeline पर निर्णय लेने और उसे किसी और को समझाने के लिए भरोसेमंद |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-what-ci-and-cd-promise.md) | CI और CD क्या वादा करते हैं | Continuous integration हर बदलाव को main पर merge और साबित रखता है, continuous delivery main को release योग्य रखती है, और continuous deployment हर pass होने वाला बदलाव ship करता है |
| [0002](lessons/0002-pipelines-as-code.md) | Code के रूप में Pipelines | Repository में workflow file उसी code की तरह version, review और run होती है जिसे वह build करती है, और Jenkins और GitLab वही विचार व्यक्त करते हैं |
| [0003](lessons/0003-triggers-and-events.md) | Triggers और Events | Workflow को push, pull request, schedule पर या हाथ से शुरू करें, उसे branch और path से filter करें, और जानें कि हर event किस commit पर चलता है |
| [0004](lessons/0004-jobs-steps-and-runners.md) | Jobs, Steps और Runners | Jobs नए runners पर parallel चलते हैं जब तक needs उन्हें क्रम न दे, steps एक workspace साझा करते हैं, और hosted और self-hosted runners नियंत्रण के बदले क़ीमत देते हैं |
| [0005](lessons/0005-actions-expressions-and-outputs.md) | Actions, Expressions और Outputs | uses से action को दोबारा इस्तेमाल करें, contexts पर if और expressions से निर्णय लें, और outputs से steps और jobs के बीच मान पास करें |
| [0006](lessons/0006-build-and-test-stages.md) | Build और Test Stages | Lint, build, unit और integration stages को ऐसे क्रम दें कि सबसे सस्ती विफलता पहले आए, उन tests के लिए service containers के साथ जिन्हें database चाहिए |
| [0007](lessons/0007-matrix-builds.md) | Matrix Builds | Matrix से एक job को versions और platforms पर चलाएँ, और नियंत्रित करें कि fail-fast, include और exclude run के साथ क्या करते हैं |
| [0008](lessons/0008-caching.md) | Caching | Cache की key lockfile पर रखें, restore keys से fallback करें, और जानें कि cache पर किस चीज़ को रखने के लिए कभी भरोसा नहीं करना चाहिए |
| [0009](lessons/0009-flaky-tests.md) | Flaky Tests | बिना code बदलाव के fail होने वाला test पूरी pipeline पर भरोसा नष्ट कर देता है, इसलिए उसे retries के पीछे छिपाने के बजाय उसका कारण ढूँढें और उसे quarantine करें |
| [0010](lessons/0010-making-a-pipeline-fast.md) | Pipeline को तेज़ बनाना | Critical path छोटा करें, concurrency groups से पुराने पड़ चुके runs रद्द करें, और timeouts सेट करें ताकि अटका job queue को रोक न सके |
| [0011](lessons/0011-artifacts.md) | Artifacts | Artifacts से build output को jobs के बीच पास करें और run के बाद रखें, और artifact cache क्यों नहीं है |
| [0012](lessons/0012-versioning-a-build.md) | Build की Versioning | हर build को उसके commit तक trace होने वाली पहचान दें, और उसे एक बार build करें ताकि जो परखा गया वही ship हो |
| [0013](lessons/0013-building-and-publishing-an-image.md) | Image Build और Publish करना | Workflow से container image build, tag और push करें, उसकी layers cache करें, और बाद के stages को उसका digest सौंपें |
| [0014](lessons/0014-secrets-and-the-github-token.md) | Secrets और GITHUB_TOKEN | Secrets को हर repository और environment के हिसाब से store करें, जानें कि masking क्या चूक जाता है, और permissions से GITHUB_TOKEN को छोटा करें |
| [0015](lessons/0015-oidc-instead-of-long-lived-keys.md) | लंबे समय तक चलने वाली Keys के बजाय OIDC | Cloud को एक run के लिए जारी किए गए अल्पकालिक token पर भरोसा करने दें, और subject claim से उस भरोसे का दायरा तय करें |
| [0016](lessons/0016-untrusted-input.md) | Untrusted Input | Titles, branch names और fork का code हमलावर का input हैं, और fork के checkout के साथ pull_request_target उन्हें आपके secrets सौंप देता है |
| [0017](lessons/0017-environments-and-approvals.md) | Environments और Approvals | Environments, required reviewers, deployment branch rules और environment secrets से deploy पर रोक लगाएँ |
| [0018](lessons/0018-promotion-between-environments.md) | Environments के बीच Promotion | एक build किए गए artifact को digest से staging से production तक ले जाएँ, हर environment के लिए दिए गए configuration के साथ |
| [0019](lessons/0019-deployment-strategies.md) | Deployment रणनीतियाँ | Recreate, rolling, blue-green और canary, हर एक की क्षमता और जोखिम में क़ीमत, और canary को कुछ मायने रखने के लिए क्या मापना चाहिए |
| [0020](lessons/0020-rollback-and-roll-forward.md) | Rollback और Roll Forward | आख़िरी अच्छे artifact को फिर से deploy करके roll back करें, data आगे बढ़ चुका हो तो roll forward करें, और flags से deploy को release से अलग करें |
| [0021](lessons/0021-database-migrations-in-a-deploy.md) | Deploy में Database Migrations | Expand और contract से schema बदलावों को code के इर्द-गिर्द क्रम दें ताकि deploy के दौरान चल रहा हर version schema के साथ काम करे |
| [0022](lessons/0022-push-deploys-and-gitops.md) | Push Deploys और GitOps | Cluster में push करने वाली pipeline बनाम cluster के भीतर Git से pull करने वाला agent, और हर एक credentials और drift के साथ क्या करता है |
| [0023](lessons/0023-pinning-what-the-pipeline-runs.md) | Pipeline जो चलाती है उसे Pin करना | Third-party actions को पूरे commit SHA पर pin करें, dependencies lock करें, और Dependabot से pins को ताज़ा रखें |
| [0024](lessons/0024-provenance-and-sboms.md) | Provenance और SBOMs | Attest करें कि artifact कहाँ और किससे build हुआ, उसके भीतर क्या है उसकी सूची बनाएँ, और उसके चलने से पहले दोनों सत्यापित करें |
| [0025](lessons/0025-reusable-workflows-and-composite-actions.md) | Reusable Workflows और Composite Actions | Called workflow या composite action से pipeline logic को repositories के बीच साझा करें, और इस आधार पर चुनें कि हर एक क्या रख सकता है |
| [0026](lessons/0026-monorepos-and-path-filters.md) | Monorepos और Path Filters | Path filters से सिर्फ़ वही चलाएँ जिसे बदलाव छूता है, और skip हुआ required check हर merge को क्यों रोक सकता है |
| [0027](lessons/0027-debugging-a-pipeline.md) | Pipeline को Debug करना | Log पढ़ें, debug logging के साथ फिर से चलाएँ, और local पर pass होने पर पता लगाएँ कि runner और आपकी machine में क्या फ़र्क़ है |
| [0028](lessons/0028-reviewing-a-pipeline.md) | Pipeline की समीक्षा | किसी और के workflow की समीक्षा, यह बताकर कि सबसे पहले क्या fail होगा, धीमा होगा या leak होगा |
| [0029](lessons/0029-changing-a-shared-workflow.md) | साझा Workflow बदलना | ऐसे reusable workflow या required check को बदलें जिस पर दूसरी teams निर्भर हैं, उनके merges तोड़े बिना |
| [0030](lessons/0030-when-the-usual-answer-is-wrong.md) | जब आम जवाब ग़लत हो | बताएँ कि कब continuous deployment, canary या pipeline का कोई default ग़लत निर्णय है, और विवादित व्यवहार को workflow syntax reference से तय करें |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत, हर एक के साथ टिप्पणी कि वह क्या कवर करता है
- [Workflow Syntax](reference/workflow-syntax.md): triggers, jobs, steps, expressions, contexts और outputs, Jenkins और GitLab के समकक्षों के साथ, चरण 1 और 2 से
- [तेज़ Feedback](reference/fast-feedback.md): stages का क्रम, matrices, cache keys, flaky tests को संभालना, concurrency और timeouts, चरण 3 से
- [Artifacts और Versioning](reference/artifacts-and-versioning.md): artifacts बनाम caches, version schemes, एक बार build करना, image tags और digests, चरण 4 से
- [Pipeline Security](reference/pipeline-security.md): secrets, token permissions, OIDC, untrusted input, pinning और provenance, चरण 5 और 8 से
- [Deployments](reference/deployments.md): environments, promotion, चार रणनीतियाँ, rollback, migrations का क्रम और GitOps, चरण 6 और 7 से
- [बड़े पैमाने पर Pipelines](reference/pipelines-at-scale.md): reusable workflows बनाम composite actions, path filters, required checks और किसी run को debug करना, चरण 9 से
- [Pipeline समीक्षा Checklist](reference/pipeline-review-checklist.md): किसी और की pipeline से पूछे जाने वाले सवाल, और कब आम जवाब ग़लत है, चरण 10 से

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
