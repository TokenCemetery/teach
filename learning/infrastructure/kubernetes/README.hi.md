---
title: Kubernetes
description: "Kubernetes cluster पर services चलाएँ और उन्हें अपने हाथ में लें: reconciliation loop, workloads, networking, configuration, reliability, security, packaging और debugging"
type: topic
---

# सीखना: Kubernetes

किसी भी containerized service को Kubernetes cluster पर चलाएँ और वहाँ उसके साथ जो होता है उसकी ज़िम्मेदारी लें: उसे ऐसे manifests में बताएँ जिन्हें cluster reconcile करे, उसे expose करें, configure करें, rollouts, node failures और load के दौरान उसे healthy रखें, उसे सुरक्षित करें, कई environments के लिए package करें, और जब वह टूटे तो पता लगाएँ कि क्यों। अंत में किसी और के manifests की समीक्षा हर चुनाव की क़ीमत का नाम लेकर कर सकें, जिस पर दूसरी teams निर्भर हैं उसे उन्हें तोड़े बिना upgrade कर सकें, और बता सकें कि कब किसी service को Kubernetes की ज़रूरत ही नहीं है।

**नवीनतम पाठ:** [28. जब Kubernetes ग़लत जवाब हो](lessons/0028-when-kubernetes-is-the-wrong-answer.md)

## सफलता कैसी दिखती है

- Declarative model समझाएँ: API server के ज़रिए store की गई desired state, cluster को उसकी ओर reconcile करते controllers, और pod delete होने या node के मरने पर इसका क्या मतलब है।
- Manifests पढ़ें और लिखें: हर object के fields, labels और selectors, namespaces, और `kubectl apply` से बदलाव लागू करना।
- Deployment से stateless service चलाएँ, नया version roll out करें और उसे roll back करें, और Jobs, CronJobs और DaemonSets से batch काम और हर node के agents चलाएँ।
- Service और cluster DNS से service को cluster के भीतर expose करें, और Ingress या Gateway API से उसके बाहर।
- ConfigMaps और Secrets से workload configure करें, और बताएँ कि Secret किस चीज़ की रक्षा करता है और किसकी नहीं।
- Workload को healthy रखें: ऐसे probes जो सही सवाल का उत्तर दें, साफ़ termination, और requests और limits जो उसकी QoS class तय करें।
- Persistent storage पर stateful workloads चलाएँ, scheduling constraints से pods रखें, उन्हें अपने-आप scale करें, और voluntary disruptions को service गिराने से रोकें।
- RBAC, service accounts, network policy और pod security से workload को सुरक्षित करें।
- Kustomize या Helm से कई environments के लिए manifests package करें, और हर एक की क़ीमत के आधार पर उनमें से चुनें।
- Workload को observe करें और Pending, crash होते या पहुँच से बाहर workload को debug करें, events और logs से लेकर debug container तक।
- किसी और के manifests की समीक्षा करें, ऐसे cluster या साझा chart को upgrade करें जिस पर दूसरी teams निर्भर हैं, बताएँ कि कब Kubernetes या उसका कोई आम default ग़लत जवाब है, और विवादित सवाल को API reference से तय करें।

## सीमाएँ

- [Containers track](../containers/README.md) या उसके बराबर ज्ञान माना गया है: image build करना, एक container चलाना, एक host पर signals, health checks और सीमाएँ। Kubernetes का कोई पूर्व ज्ञान नहीं माना गया है।
- हर अभ्यास kind से बने local cluster पर चलता है, जिसके लिए Docker या Podman और कुछ gigabytes memory, साथ में `kubectl` चाहिए। Cloud account की ज़रूरत नहीं है। जहाँ किसी पाठ का व्यवहार cloud provider पर निर्भर है (`LoadBalancer` Service, node autoscaler, cloud storage class), वहाँ पाठ यह बताता है और वह हिस्सा सिखाता है जो kind दिखा सकता है।
- Upstream Kubernetes और उसके documentation का इस्तेमाल होता है। Managed offerings (EKS, GKE, AKS) defaults और add-ons में अलग हैं, और पाठ किसी फ़र्क़ का नाम सिर्फ़ वहीं लेते हैं जहाँ वह जवाब बदल देता है।

## दायरे से बाहर

- एक container build करना और चलाना। यह [containers track](../containers/README.md) है, जिसकी [Containers चलाना](../containers/reference/running-containers.md) sheet यहाँ के चरण 5 का single-host रूप है।
- Service को उसके अपने code के भीतर से observable और रोकने योग्य बनाना: health endpoints, signal handling, graceful shutdown। यह भाषा वाले tracks का हिस्सा है, जैसे Go का [Graceful Shutdown](../../programming/golang/lessons/0025-graceful-shutdown.md) और C# का [Logging और Health Checks](../../programming/csharp/lessons/0039-logging-and-health-checks.md)। यह track सिखाता है कि cluster उन संकेतों के साथ क्या करता है।
- सिद्धांत के रूप में consensus और partial failure। यह [Distributed Systems](../../architecture/distributed-systems/README.md) है, जिसकी [Consensus](../../architecture/distributed-systems/reference/consensus.md) sheet समझाती है कि नीचे etcd क्या कर रहा है। यह track सिखाता है कि workloads चलाने वाले के लिए reconciliation और etcd का क्या मतलब है।
- Pipeline से cluster तक बदलाव पहुँचाना, और GitOps tools। यह [CI/CD track](../ci-cd/README.md) है, जिसकी [Deployments](../ci-cd/reference/deployments.md) sheet deployment रणनीतियाँ, rollback और push deploy व GitOps में से चुनना कवर करती है।
- Control plane को ख़ुद install करना और चलाना (etcd backups, certificate rotation, शुरू से cluster बनाना), controllers या operators लिखना, और service meshes।

## पूरी रूपरेखा

दस चरण, reconciliation loop से लेकर किसी और के manifests की समीक्षा करने के विवेक तक। एक चरण में कई पाठ लगते हैं और सीमाएँ लचीली हैं; चरण पूरा तब होता है जब क्षमता आ जाए, पाठों की गिनती से नहीं।

| चरण | पाठ | क्या कवर होता है | कब पूरा माना जाए |
|---|---|---|---|
| 1. Declarative model | 0001 से 0003 | Cluster, control plane और nodes, API server, etcd और controllers, reconciliation loop, object fields, labels, namespaces, `kubectl apply` | Desired state में बदलाव के बाद cluster क्या करेगा इसका अनुमान लगा सकें, और ऐसा manifest लिख सकें जिसे वह स्वीकार करे |
| 2. Workloads | 0004 से 0007 | Pods, Deployments और ReplicaSets, rolling updates और rollbacks, Jobs, CronJobs और DaemonSets | Stateless service चला सकें, उसे आगे और पीछे roll कर सकें, और जो काम service नहीं है उसके लिए controller चुन सकें |
| 3. Networking | 0008 से 0010 | Services और EndpointSlices, kube-proxy, cluster DNS, Ingress और Gateway API | Workload को cluster के भीतर और बाहर पहुँचने योग्य बना सकें और न पहुँचने पर बता सकें कि कौन-सा hop fail हुआ |
| 4. Configuration | 0011 से 0012 | Environment और files के रूप में ConfigMaps, Secrets, encryption at rest, secrets को Git से बाहर रखना | हर environment के लिए workload configure कर सकें और बता सकें कि उसके secrets की रक्षा क्या करता है |
| 5. भरोसेमंद ढंग से चलाना | 0013 से 0015 | Liveness, readiness और startup probes, termination और endpoint race, requests, limits और QoS classes | ऐसा workload चला सकें जो तैयार होने पर ही traffic ले, साफ़ ढंग से drain हो और सबसे पहले evict होने वाला न हो |
| 6. State, scheduling और scale | 0016 से 0019 | PersistentVolumes और claims, StatefulSets, affinity, taints और topology spread, autoscaling, PodDisruptionBudgets | Stateful workload चला सकें, pods को सोच-समझकर रख सकें, और बिना outage के scale और drain कर सकें |
| 7. Security | 0020 से 0021 | RBAC, service accounts, NetworkPolicy, security contexts, Pod Security Standards | लोगों और pods को least privilege दे सकें और सीमित कर सकें कि pod कहाँ पहुँच सकता है और क्या कर सकता है |
| 8. Packaging | 0022 से 0023 | Kustomize bases और overlays, Helm charts, values और releases, उनमें से चुनना | Manifests का एक set कई environments तक ship कर सकें और चुने गए tool को सही ठहरा सकें |
| 9. Observability और debugging | 0024 से 0025 | Resource metrics, events, logs, kube-state-metrics, failure states और उन्हें समझाने वाली commands, debug containers | पता लगा सकें कि workload Pending, crash होता या पहुँच से बाहर क्यों है |
| 10. विवेक | 0026 से 0028 | Manifests की समीक्षा, ऐसे cluster या साझा chart को upgrade करना जिस पर दूसरे निर्भर हैं, कब Kubernetes या कोई default ग़लत है, API reference से उसे तय करना | Workload पर निर्णय लेने और उसे किसी और को समझाने के लिए भरोसेमंद |

## पाठ

इन्हें क्रम से करें।

| # | पाठ | क्या सिखाता है |
|---|---|---|
| [0001](lessons/0001-what-kubernetes-is-for.md) | Kubernetes किसलिए है | Cluster कई machines को containers चलाने की एक जगह में बदल देता है, और control plane और nodes काम बाँट लेते हैं |
| [0002](lessons/0002-the-reconciliation-loop.md) | Reconciliation Loop | आप API server के ज़रिए desired state घोषित करते हैं, और controllers तब तक देखते और कार्रवाई करते रहते हैं जब तक cluster उससे मेल न खाए |
| [0003](lessons/0003-objects-and-manifests.md) | Objects और Manifests | हर object में apiVersion, kind, metadata, spec और status होते हैं, और labels, selectors, namespaces और kubectl apply सब उन्हीं fields पर काम करते हैं |
| [0004](lessons/0004-pods.md) | Pods | Pod वह इकाई है जिसे cluster schedule करता है, ऐसे containers जो network namespace और volumes साझा करते हैं, और आप ख़ुद शायद ही कभी pod क्यों बनाते हैं |
| [0005](lessons/0005-deployments-and-replicasets.md) | Deployments और ReplicaSets | Deployment उन ReplicaSets का मालिक है जो pods के मालिक हैं, इसलिए delete हुआ pod बदल दिया जाता है और बदला हुआ template नया ReplicaSet बन जाता है |
| [0006](lessons/0006-rollouts-and-rollbacks.md) | Rollouts और Rollbacks | maxSurge और maxUnavailable के साथ नया version roll out करें, उस पर नज़र रखें, उसे रोकें, और जाने-पहचाने revision पर roll back करें |
| [0007](lessons/0007-jobs-cronjobs-and-daemonsets.md) | Jobs, CronJobs और DaemonSets | ख़त्म होने वाला काम, schedule पर काम, और हर node पर एक pod चलाएँ, और हर एक का failure mode |
| [0008](lessons/0008-services.md) | Services | Service बदलते pods के set को एक स्थिर virtual IP देती है, और EndpointSlices और kube-proxy तैयार pods तक route करते हैं |
| [0009](lessons/0009-cluster-dns.md) | Cluster DNS | Pod किसी Service को नाम से कैसे ढूँढता है, search path और ndots हर lookup के साथ क्या करते हैं, और headless Service क्या लौटाती है |
| [0010](lessons/0010-ingress-and-the-gateway-api.md) | Ingress और Gateway API | बाहरी HTTP traffic को controller के ज़रिए cluster में लाएँ, और Gateway API काम को role के हिसाब से क्यों बाँटता है |
| [0011](lessons/0011-configmaps.md) | ConfigMaps | Configuration को environment variables या files के रूप में inject करें, और जानें कि दोनों में से कौन restart के बिना बदलाव देखता है |
| [0012](lessons/0012-secrets.md) | Secrets | Secret base64 है, encryption नहीं, इसलिए उसकी रक्षा RBAC, encryption at rest और उसे Git से बाहर रखना करता है |
| [0013](lessons/0013-probes.md) | Probes | Liveness, readiness और startup probes अलग सवालों के उत्तर देते हैं, और ग़लत liveness probe वही outage पैदा करता है जिसे रोकने के लिए वह बना था |
| [0014](lessons/0014-pod-termination.md) | Pod Termination | Delete और SIGKILL के बीच क्या होता है, और SIGTERM के बाद भी pod को traffic क्यों मिलता है जब तक आप इसकी योजना न बनाएँ |
| [0015](lessons/0015-requests-limits-and-qos.md) | Requests, Limits और QoS | Requests scheduling चलाते हैं और limits enforcement, और मिलकर वे QoS class तय करते हैं जो तय करती है कि पहले किसे evict किया जाए |
| [0016](lessons/0016-persistent-storage.md) | Persistent Storage | PersistentVolumeClaim से storage claim करें, StorageClass को उसे provision करने दें, और जानें कि access modes और reclaim policies क्या वादा करती हैं |
| [0017](lessons/0017-statefulsets.md) | StatefulSets | स्थिर नाम, क्रम से startup और हर replica का अपना volume, और अकेला StatefulSet database चलाना सुरक्षित क्यों नहीं बनाता |
| [0018](lessons/0018-scheduling.md) | Scheduling | Node selectors, affinity, topology spread, taints और tolerations से pods को दिशा दें, और पढ़ें कि pod Pending क्यों रहता है |
| [0019](lessons/0019-autoscaling-and-disruptions.md) | Autoscaling और Disruptions | HorizontalPodAutoscaler से pods और node autoscaler से nodes scale करें, और PodDisruptionBudget से drain को बहुत ज़्यादा pods गिराने से रोकें |
| [0020](lessons/0020-rbac-and-service-accounts.md) | RBAC और Service Accounts | Roles और bindings से किसी व्यक्ति या pod को ठीक वही verbs दें जिनकी उसे ज़रूरत है, और kubectl auth can-i से उसे जाँचें |
| [0021](lessons/0021-network-policy-and-pod-security.md) | Network Policy और Pod Security | Default रूप से pods के बीच traffic deny करें, फिर security contexts और Pod Security Standards से सीमित करें कि pod अपने node पर क्या कर सकता है |
| [0022](lessons/0022-kustomize.md) | Kustomize | साधारण manifests का एक base रखें और template language के बिना overlays से हर environment के लिए उसे patch करें |
| [0023](lessons/0023-helm-against-kustomize.md) | Helm बनाम Kustomize | Helm chart install करें और लिखें, और हर एक की क़ीमत के आधार पर chart और Kustomize overlay में से चुनें |
| [0024](lessons/0024-observability.md) | Observability | Resource metrics, events, container logs और object state metrics पढ़ें, और जानें कि हर एक किस सवाल का उत्तर देता है |
| [0025](lessons/0025-debugging-a-workload.md) | Workload को Debug करना | describe, events, logs और kubectl debug के साथ Pending, ImagePullBackOff, CrashLoopBackOff और OOMKilled से कारण तक पहुँचें |
| [0026](lessons/0026-reviewing-manifests.md) | Manifests की समीक्षा | किसी और के manifests की समीक्षा, हर चुनाव की availability, security और operability में क़ीमत का नाम लेकर |
| [0027](lessons/0027-upgrading-what-others-depend-on.md) | जिस पर दूसरे निर्भर हैं उसे Upgrade करना | Cluster या साझा chart को हटाए गए API version से आगे ले जाएँ, उन teams को तोड़े बिना जिनके workloads उस पर निर्भर हैं |
| [0028](lessons/0028-when-kubernetes-is-the-wrong-answer.md) | जब Kubernetes ग़लत जवाब हो | बताएँ कि कब किसी service को Kubernetes की ज़रूरत नहीं या कोई आम default ग़लत है, और विवादित सवाल को API reference से तय करें |

## Reference

- [शब्दावली](GLOSSARY.md): इस विषय के मानक शब्द
- [संसाधन](RESOURCES.md): भरोसेमंद स्रोत, हर एक के साथ टिप्पणी कि वह क्या कवर करता है
- [kubectl](reference/kubectl.md): काम के हिसाब से commands, objects की जाँच से लेकर rollouts, debugging और permission checks तक, पूरी रूपरेखा में
- [Workloads](reference/workloads.md): object fields, labels और selectors, pods, Deployments, rollouts, Jobs, CronJobs और DaemonSets, चरण 1 और 2 से
- [Networking](reference/networking.md): Service types, EndpointSlices, DNS names और ndots, Ingress और Gateway API resources, चरण 3 से
- [Configuration](reference/configuration.md): environment और files के रूप में ConfigMaps और Secrets, update का व्यवहार, और Secret की रक्षा क्या करता है, चरण 4 से
- [भरोसेमंद ढंग से चलाना](reference/running-reliably.md): तीन probes, termination का क्रम, requests, limits और QoS classes, चरण 5 से
- [State, Scheduling और Scale](reference/state-scheduling-and-scale.md): storage, StatefulSets, placement constraints, autoscalers और disruption budgets, चरण 6 से
- [Cluster Security](reference/cluster-security.md): RBAC objects, service account tokens, NetworkPolicy patterns और Pod Security Standards, चरण 7 से
- [Packaging](reference/packaging.md): Kustomize और Helm साथ-साथ, और हर एक कब फ़िट होता है, चरण 8 से
- [Workloads को Debug करना](reference/debugging-workloads.md): हर failure state, उसका कारण और क्रम से चलाने वाली commands, चरण 9 से
- [Manifest समीक्षा Checklist](reference/manifest-review-checklist.md): किसी और के manifests से पूछे जाने वाले सवाल, और कब आम जवाब ग़लत है, चरण 10 से

## यह कैसे काम करता है

हर पाठ छोटा और अपने-आप में पूरा है। उत्तर कुंजियाँ बंद रहती हैं: पहले याद करें, फिर खोलें। असली दुनिया का अभ्यास पढ़ने से ज़्यादा मायने रखता है, और उसे समय के अंतराल पर करना ही मक़सद है। पाठ के अंत में जो कुछ अब भी साफ़ न हो, उसे आगे बढ़ने से पहले उसके primary source तक खंगालना ठीक रहेगा।
